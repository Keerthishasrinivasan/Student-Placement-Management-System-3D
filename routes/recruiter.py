from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime
from models import db, User, Company, JobPosting, Application, StudentProfile

recruiter_bp = Blueprint('recruiter', __name__, url_prefix='/recruiter')

def recruiter_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this recruiter portal.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'recruiter':
            flash('Access restricted to Recruiters.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_company():
    user = User.query.get(session.get('user_id'))
    if user and user.company:
        return user.company
    # Fallback to first company if recruiter is demo
    return Company.query.first()


@recruiter_bp.route('/dashboard')
@recruiter_required
def dashboard():
    company = get_current_company()
    if not company:
        flash('No company profile associated with this recruiter account.', 'warning')
        return redirect(url_for('main.index'))

    jobs = JobPosting.query.filter_by(company_id=company.id).order_by(JobPosting.created_at.desc()).all()
    job_ids = [j.id for j in jobs]
    
    applications = Application.query.filter(Application.job_id.in_(job_ids)).order_by(Application.applied_date.desc()).all() if job_ids else []
    
    total_applicants = len(applications)
    shortlisted_count = sum(1 for a in applications if a.status in ['Shortlisted', 'Aptitude Test', 'Technical Interview', 'HR Interview'])
    offered_count = sum(1 for a in applications if a.status in ['Offered', 'Accepted'])

    return render_template(
        'recruiter/dashboard.html',
        company=company,
        jobs=jobs,
        applications=applications[:8],
        total_applicants=total_applicants,
        shortlisted_count=shortlisted_count,
        offered_count=offered_count
    )


@recruiter_bp.route('/jobs/new', methods=['GET', 'POST'])
@recruiter_required
def post_job():
    company = get_current_company()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        job_type = request.form.get('job_type', 'Full Time')
        package_lpa = float(request.form.get('package_lpa', 10.0))
        stipend_pm = int(request.form.get('stipend_pm', 0) or 0)
        location = request.form.get('location', 'Bengaluru')
        min_cgpa = float(request.form.get('min_cgpa', 7.0))
        max_backlogs = int(request.form.get('max_backlogs', 0))
        eligible_depts = request.form.get('eligible_departments', 'CSE, IT, ECE')
        skills = request.form.get('skills_required', 'Python, SQL, Algorithms')
        description = request.form.get('description', '')
        responsibilities = request.form.get('responsibilities', '')
        selection_process = request.form.get('selection_process', 'Online Test -> Technical Rounds -> HR Interview')
        deadline_str = request.form.get('deadline')
        
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else datetime.utcnow()
        except ValueError:
            deadline = datetime.utcnow()

        job = JobPosting(
            company_id=company.id,
            title=title,
            job_type=job_type,
            package_lpa=package_lpa,
            stipend_pm=stipend_pm,
            location=location,
            min_cgpa=min_cgpa,
            max_backlogs=max_backlogs,
            eligible_departments=eligible_depts,
            skills_required=skills,
            description=description,
            responsibilities=responsibilities,
            selection_process=selection_process,
            deadline=deadline,
            status='Open'
        )
        db.session.add(job)
        db.session.commit()

        flash(f'Job opening for "{title}" published successfully!', 'success')
        return redirect(url_for('recruiter.dashboard'))

    return render_template('recruiter/post_job.html', company=company)


@recruiter_bp.route('/jobs/<int:job_id>/applicants')
@recruiter_required
def applicants(job_id):
    company = get_current_company()
    job = JobPosting.query.filter_by(id=job_id, company_id=company.id).first_or_404()
    
    # Filter applicants
    status_filter = request.args.get('status', '')
    min_cgpa_filter = request.args.get('min_cgpa', type=float)

    query = Application.query.filter_by(job_id=job.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    apps = query.join(StudentProfile).order_by(StudentProfile.cgpa.desc()).all()
    if min_cgpa_filter:
        apps = [a for a in apps if a.student.cgpa >= min_cgpa_filter]

    return render_template(
        'recruiter/applicants.html',
        company=company,
        job=job,
        applications=apps,
        status_filter=status_filter
    )


@recruiter_bp.route('/applications/<int:app_id>/status', methods=['POST'])
@recruiter_required
def update_application_status(app_id):
    application = Application.query.get_or_404(app_id)
    new_status = request.form.get('status')
    interview_date_str = request.form.get('interview_date')
    interview_link = request.form.get('interview_link')
    recruiter_notes = request.form.get('recruiter_notes')

    if new_status:
        application.status = new_status
        # Update stage index
        stage_map = {
            'Applied': 1,
            'Shortlisted': 2,
            'Aptitude Test': 3,
            'Technical Interview': 4,
            'HR Interview': 5,
            'Offered': 6,
            'Rejected': 0,
            'Accepted': 6
        }
        application.current_round_index = stage_map.get(new_status, application.current_round_index)

    if interview_date_str:
        try:
            application.interview_date = datetime.strptime(interview_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            pass
    if interview_link:
        application.interview_link = interview_link
    if recruiter_notes:
        application.recruiter_notes = recruiter_notes

    db.session.commit()
    flash(f"Application status for {application.student.user.full_name} updated to '{application.status}'.", 'success')
    return redirect(url_for('recruiter.applicants', job_id=application.job_id))
