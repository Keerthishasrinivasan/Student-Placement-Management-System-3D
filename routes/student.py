from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from datetime import datetime
from models import db, User, StudentProfile, JobPosting, Company, Application, MockAssessment, AssessmentQuestion, AssessmentResult, Announcement

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this portal.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'student':
            flash('Access restricted to Students.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_student():
    """Helper to retrieve current student profile."""
    user = User.query.get(session.get('user_id'))
    if user and user.student_profile:
        return user.student_profile
    return None


@student_bp.route('/dashboard')
@student_required
def dashboard():
    student = get_current_student()
    if not student:
        flash('Student profile not found. Please complete your registration.', 'warning')
        return redirect(url_for('auth.login'))

    # Active applications
    applications = Application.query.filter_by(student_id=student.id).order_by(Application.updated_at.desc()).all()
    
    # Counts
    total_applied = len(applications)
    shortlisted_count = sum(1 for a in applications if a.status in ['Shortlisted', 'Aptitude Test', 'Technical Interview', 'HR Interview'])
    offers_count = sum(1 for a in applications if a.status in ['Offered', 'Accepted'])

    # Eligible open jobs
    open_jobs = JobPosting.query.filter_by(status='Open').all()
    eligible_jobs = []
    applied_job_ids = {a.job_id for a in applications}

    for job in open_jobs:
        if job.id not in applied_job_ids:
            eligible, _ = job.is_student_eligible(student)
            if eligible:
                eligible_jobs.append(job)

    # Announcements
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()

    # Recent assessment scores
    recent_assessments = AssessmentResult.query.filter_by(student_id=student.id).order_by(AssessmentResult.completed_at.desc()).limit(3).all()

    return render_template(
        'student/dashboard.html',
        student=student,
        applications=applications[:5],
        total_applied=total_applied,
        shortlisted_count=shortlisted_count,
        offers_count=offers_count,
        recommended_jobs=eligible_jobs[:4],
        announcements=announcements,
        recent_assessments=recent_assessments
    )


@student_bp.route('/jobs')
@student_required
def jobs():
    student = get_current_student()
    
    # Query parameters for filtering
    search = request.args.get('search', '').strip()
    job_type = request.args.get('job_type', '')
    department = request.args.get('department', '')
    min_package = request.args.get('min_package', type=float)
    max_backlogs = request.args.get('max_backlogs', type=int)
    tier = request.args.get('tier', '')

    query = JobPosting.query.filter_by(status='Open')

    if search:
        query = query.join(Company).filter(
            (JobPosting.title.ilike(f'%{search}%')) |
            (Company.name.ilike(f'%{search}%')) |
            (JobPosting.skills_required.ilike(f'%{search}%'))
        )
    if job_type:
        query = query.filter(JobPosting.job_type == job_type)
    if min_package:
        query = query.filter(JobPosting.package_lpa >= min_package)
    if max_backlogs is not None:
        query = query.filter(JobPosting.max_backlogs >= max_backlogs)
    if tier:
        query = query.join(Company).filter(Company.tier == tier)

    jobs_list = query.order_by(JobPosting.created_at.desc()).all()

    # Map application statuses
    user_applications = {a.job_id: a for a in Application.query.filter_by(student_id=student.id).all()}

    # Compute eligibility & match for each job
    enriched_jobs = []
    for j in jobs_list:
        is_eligible, reason = j.is_student_eligible(student)
        
        # Skill match percentage
        student_skills = set(s.lower() for s in student.skill_list)
        req_skills = set(s.lower() for s in j.skill_req_list)
        match_pct = 50
        if req_skills:
            common = student_skills.intersection(req_skills)
            match_pct = int((len(common) / len(req_skills)) * 100)
            match_pct = max(30, min(100, match_pct))

        app = user_applications.get(j.id)
        enriched_jobs.append({
            'job': j,
            'is_eligible': is_eligible,
            'eligibility_reason': reason,
            'match_pct': match_pct,
            'application': app
        })

    return render_template(
        'student/jobs.html',
        student=student,
        jobs=enriched_jobs,
        search=search,
        job_type=job_type,
        min_package=min_package,
        tier=tier
    )


@student_bp.route('/jobs/<int:job_id>')
@student_required
def job_detail(job_id):
    student = get_current_student()
    job = JobPosting.query.get_or_404(job_id)
    application = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
    is_eligible, reason = job.is_student_eligible(student)

    # Calculate skill match details
    student_skills = [s.strip() for s in student.skill_list]
    student_skills_lower = [s.lower() for s in student_skills]
    req_skills = [s.strip() for s in job.skill_req_list]
    
    matched_skills = [s for s in req_skills if s.lower() in student_skills_lower]
    missing_skills = [s for s in req_skills if s.lower() not in student_skills_lower]
    
    match_pct = int((len(matched_skills) / len(req_skills) * 100)) if req_skills else 80

    return render_template(
        'student/job_detail.html',
        student=student,
        job=job,
        application=application,
        is_eligible=is_eligible,
        eligibility_reason=reason,
        match_pct=match_pct,
        matched_skills=matched_skills,
        missing_skills=missing_skills
    )


@student_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
@student_required
def apply_job(job_id):
    student = get_current_student()
    job = JobPosting.query.get_or_404(job_id)

    # Check already applied
    existing = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
    if existing:
        flash(f'You have already applied for {job.title} at {job.company.name}.', 'info')
        return redirect(url_for('student.applications'))

    # Check eligibility
    is_eligible, reason = job.is_student_eligible(student)
    if not is_eligible:
        flash(f'Application rejected: {reason}', 'error')
        return redirect(url_for('student.job_detail', job_id=job.id))

    # Calculate skill match percentage
    student_skills_lower = [s.lower() for s in student.skill_list]
    req_skills = [s.strip() for s in job.skill_req_list]
    matched = [s for s in req_skills if s.lower() in student_skills_lower]
    match_pct = int((len(matched) / len(req_skills) * 100)) if req_skills else 85
    match_pct = max(45, min(98, match_pct))

    application = Application(
        job_id=job.id,
        student_id=student.id,
        status='Applied',
        current_round_index=1,
        match_percentage=match_pct
    )
    db.session.add(application)
    db.session.commit()

    flash(f'Successfully applied for {job.title} at {job.company.name}!', 'success')
    return redirect(url_for('student.applications'))


@student_bp.route('/applications')
@student_required
def applications():
    student = get_current_student()
    apps = Application.query.filter_by(student_id=student.id).order_by(Application.updated_at.desc()).all()

    # Stages definition for the visual timeline / Kanban tracker
    stages = [
        {'name': 'Applied', 'index': 1, 'badge': 'bg-blue'},
        {'name': 'Shortlisted', 'index': 2, 'badge': 'bg-purple'},
        {'name': 'Aptitude Test', 'index': 3, 'badge': 'bg-amber'},
        {'name': 'Technical Interview', 'index': 4, 'badge': 'bg-indigo'},
        {'name': 'HR Interview', 'index': 5, 'badge': 'bg-cyan'},
        {'name': 'Offered', 'index': 6, 'badge': 'bg-emerald'}
    ]

    return render_template(
        'student/applications.html',
        student=student,
        applications=apps,
        stages=stages
    )


@student_bp.route('/applications/<int:app_id>/accept', methods=['POST'])
@student_required
def accept_offer(app_id):
    student = get_current_student()
    application = Application.query.filter_by(id=app_id, student_id=student.id).first_or_404()

    if application.status != 'Offered':
        flash('Only offered applications can be accepted.', 'error')
        return redirect(url_for('student.applications'))

    application.status = 'Accepted'
    student.placement_status = 'Placed'
    db.session.commit()

    flash(f'Congratulations! You have accepted the offer from {application.job.company.name} ({application.job.package_lpa} LPA)!', 'success')
    return redirect(url_for('student.applications'))


@student_bp.route('/applications/<int:app_id>/decline', methods=['POST'])
@student_required
def decline_offer(app_id):
    student = get_current_student()
    application = Application.query.filter_by(id=app_id, student_id=student.id).first_or_404()

    if application.status != 'Offered':
        flash('Only offered applications can be declined.', 'error')
        return redirect(url_for('student.applications'))

    application.status = 'Declined'
    db.session.commit()

    flash(f'You have declined the offer from {application.job.company.name}.', 'info')
    return redirect(url_for('student.applications'))


@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student = get_current_student()
    user = student.user

    if request.method == 'POST':
        user.full_name = request.form.get('full_name', user.full_name).strip()
        user.phone = request.form.get('phone', user.phone).strip()

        student.department = request.form.get('department', student.department)
        student.batch_year = int(request.form.get('batch_year', student.batch_year))
        student.cgpa = float(request.form.get('cgpa', student.cgpa))
        student.tenth_percentage = float(request.form.get('tenth_percentage', student.tenth_percentage))
        student.twelfth_percentage = float(request.form.get('twelfth_percentage', student.twelfth_percentage))
        student.active_backlogs = int(request.form.get('active_backlogs', student.active_backlogs))
        student.skills = request.form.get('skills', student.skills).strip()
        student.dream_company = request.form.get('dream_company', student.dream_company).strip()
        student.preferred_role = request.form.get('preferred_role', student.preferred_role).strip()
        student.bio = request.form.get('bio', student.bio).strip()
        student.github_url = request.form.get('github_url', student.github_url).strip()
        student.linkedin_url = request.form.get('linkedin_url', student.linkedin_url).strip()

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', student=student, user=user)


@student_bp.route('/resume-analyzer')
@student_required
def resume_analyzer():
    student = get_current_student()
    jobs = JobPosting.query.filter_by(status='Open').all()
    return render_template('student/resume_analyzer.html', student=student, jobs=jobs)


@student_bp.route('/mock-interview')
@student_required
def mock_interview():
    student = get_current_student()
    return render_template('student/mock_interview.html', student=student)


@student_bp.route('/assessments')
@student_required
def assessments():
    student = get_current_student()
    all_assessments = MockAssessment.query.all()
    past_results = {r.assessment_id: r for r in AssessmentResult.query.filter_by(student_id=student.id).all()}
    
    return render_template(
        'student/assessments.html',
        student=student,
        assessments=all_assessments,
        past_results=past_results
    )


@student_bp.route('/assessments/<int:assessment_id>')
@student_required
def take_assessment(assessment_id):
    student = get_current_student()
    assessment = MockAssessment.query.get_or_404(assessment_id)
    questions = assessment.questions.all()
    
    return render_template(
        'student/take_assessment.html',
        student=student,
        assessment=assessment,
        questions=questions
    )


@student_bp.route('/assessments/<int:assessment_id>/submit', methods=['POST'])
@student_required
def submit_assessment(assessment_id):
    student = get_current_student()
    assessment = MockAssessment.query.get_or_404(assessment_id)
    questions = assessment.questions.all()

    score = 0
    total = len(questions)

    for q in questions:
        user_answer = request.form.get(f'question_{q.id}')
        if user_answer and user_answer.strip().upper() == q.correct_option.strip().upper():
            score += 1

    percentage = round((score / total) * 100, 1) if total > 0 else 0

    # Save or update result
    result = AssessmentResult.query.filter_by(student_id=student.id, assessment_id=assessment.id).first()
    if not result:
        result = AssessmentResult(
            student_id=student.id,
            assessment_id=assessment.id,
            score=score,
            total_marks=total,
            percentage=percentage,
            time_taken_seconds=300
        )
        db.session.add(result)
    else:
        result.score = score
        result.total_marks = total
        result.percentage = percentage
        result.completed_at = datetime.utcnow()

    db.session.commit()
    flash(f'Assessment completed! Your score: {score}/{total} ({percentage}%)', 'success')
    return redirect(url_for('student.assessments'))
