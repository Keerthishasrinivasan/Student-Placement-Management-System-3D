import csv
from io import StringIO
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from functools import wraps
from models import db, User, StudentProfile, Company, JobPosting, Application, PlacementDrive, Announcement

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as an administrator.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Access restricted to Placement Administrators.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_students = StudentProfile.query.count()
    placed_students = StudentProfile.query.filter_by(placement_status='Placed').count()
    in_process_students = StudentProfile.query.filter_by(placement_status='In Process').count()
    unplaced_students = StudentProfile.query.filter_by(placement_status='Unplaced').count()
    
    placement_rate = round((placed_students / total_students * 100), 1) if total_students > 0 else 0
    
    total_companies = Company.query.count()
    total_jobs = JobPosting.query.count()
    active_jobs = JobPosting.query.filter_by(status='Open').count()
    total_applications = Application.query.count()
    
    # Highest & average package
    highest_job = JobPosting.query.order_by(JobPosting.package_lpa.desc()).first()
    highest_ctc = highest_job.package_lpa if highest_job else 44.0
    
    # Calculate average CTC from all jobs
    jobs = JobPosting.query.all()
    avg_ctc = round(sum(j.package_lpa for j in jobs) / len(jobs), 2) if jobs else 12.4

    # Upcoming drives
    upcoming_drives = PlacementDrive.query.order_by(PlacementDrive.drive_date.asc()).limit(5).all()
    
    # Recent announcements
    recent_announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()

    # Recent applications
    recent_applications = Application.query.order_by(Application.applied_date.desc()).limit(6).all()

    stats = {
        'total_students': total_students,
        'placed_students': placed_students,
        'in_process_students': in_process_students,
        'unplaced_students': unplaced_students,
        'placement_rate': placement_rate,
        'total_companies': total_companies,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'highest_ctc': highest_ctc,
        'avg_ctc': avg_ctc
    }

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        upcoming_drives=upcoming_drives,
        recent_announcements=recent_announcements,
        recent_applications=recent_applications
    )


@admin_bp.route('/students')
@admin_required
def students():
    department = request.args.get('department', '')
    min_cgpa = request.args.get('min_cgpa', type=float)
    max_backlogs = request.args.get('max_backlogs', type=int)
    placement_status = request.args.get('status', '')
    search = request.args.get('search', '').strip()

    query = StudentProfile.query.join(User)

    if department:
        query = query.filter(StudentProfile.department == department)
    if min_cgpa:
        query = query.filter(StudentProfile.cgpa >= min_cgpa)
    if max_backlogs is not None:
        query = query.filter(StudentProfile.active_backlogs <= max_backlogs)
    if placement_status:
        query = query.filter(StudentProfile.placement_status == placement_status)
    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (StudentProfile.roll_number.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )

    student_list = query.order_by(StudentProfile.cgpa.desc()).all()
    
    # Distinct departments for filter dropdown
    all_depts = [d[0] for d in db.session.query(StudentProfile.department).distinct().all()]

    return render_template(
        'admin/students.html',
        students=student_list,
        departments=all_depts,
        selected_dept=department,
        min_cgpa=min_cgpa,
        max_backlogs=max_backlogs,
        selected_status=placement_status,
        search=search,
        total_count=len(student_list)
    )


@admin_bp.route('/students/export-csv')
@admin_required
def export_students_csv():
    """Export filtered student database to CSV format."""
    department = request.args.get('department', '')
    min_cgpa = request.args.get('min_cgpa', type=float)
    max_backlogs = request.args.get('max_backlogs', type=int)
    placement_status = request.args.get('status', '')

    query = StudentProfile.query.join(User)

    if department:
        query = query.filter(StudentProfile.department == department)
    if min_cgpa:
        query = query.filter(StudentProfile.cgpa >= min_cgpa)
    if max_backlogs is not None:
        query = query.filter(StudentProfile.active_backlogs <= max_backlogs)
    if placement_status:
        query = query.filter(StudentProfile.placement_status == placement_status)

    students = query.order_by(StudentProfile.roll_number.asc()).all()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Roll Number', 'Full Name', 'Email', 'Phone', 'Department', 'CGPA', '10th %', '12th %', 'Active Backlogs', 'Skills', 'Placement Status', 'Dream Company'])

    for s in students:
        cw.writerow([
            s.roll_number,
            s.user.full_name,
            s.user.email,
            s.user.phone or '',
            s.department,
            s.cgpa,
            s.tenth_percentage,
            s.twelfth_percentage,
            s.active_backlogs,
            s.skills,
            s.placement_status,
            s.dream_company
        ])

    output = si.getvalue()
    si.close()

    filename = f"placement_eligible_students_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )


@admin_bp.route('/companies', methods=['GET', 'POST'])
@admin_required
def companies():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip().upper()
        industry = request.form.get('industry', 'Information Technology')
        tier = request.form.get('tier', 'Dream')
        website = request.form.get('website', '')
        location = request.form.get('location', 'Bengaluru')
        hr_name = request.form.get('hr_name', '')
        hr_email = request.form.get('hr_email', '')
        description = request.form.get('description', '')

        if not name or not code:
            flash('Company name and short code are required.', 'error')
            return redirect(url_for('admin.companies'))

        if Company.query.filter_by(name=name).first() or Company.query.filter_by(code=code).first():
            flash('A company with this name or code already exists.', 'error')
            return redirect(url_for('admin.companies'))

        comp = Company(
            name=name,
            code=code,
            industry=industry,
            tier=tier,
            website=website,
            location=location,
            hr_name=hr_name,
            hr_email=hr_email,
            description=description
        )
        db.session.add(comp)
        db.session.commit()
        flash(f'Company "{name}" registered successfully!', 'success')
        return redirect(url_for('admin.companies'))

    all_companies = Company.query.order_by(Company.name.asc()).all()
    return render_template('admin/companies.html', companies=all_companies)


@admin_bp.route('/drives', methods=['GET', 'POST'])
@admin_required
def drives():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company_id = int(request.form.get('company_id'))
        drive_date_str = request.form.get('drive_date')
        venue = request.form.get('venue', 'Main Auditorium')
        mode = request.form.get('mode', 'Hybrid')
        rounds = request.form.get('rounds_summary', 'Aptitude -> Coding -> Technical -> HR')
        eligibility = request.form.get('eligibility_summary', 'CGPA >= 7.0, No backlogs')

        try:
            drive_date = datetime.strptime(drive_date_str, '%Y-%m-%d')
        except ValueError:
            drive_date = datetime.utcnow()

        drive = PlacementDrive(
            company_id=company_id,
            title=title,
            drive_date=drive_date,
            venue=venue,
            mode=mode,
            rounds_summary=rounds,
            eligibility_summary=eligibility,
            status='Scheduled'
        )
        db.session.add(drive)
        db.session.commit()
        flash(f'Placement Drive "{title}" scheduled successfully!', 'success')
        return redirect(url_for('admin.drives'))

    all_drives = PlacementDrive.query.order_by(PlacementDrive.drive_date.desc()).all()
    all_companies = Company.query.order_by(Company.name.asc()).all()
    return render_template('admin/drives.html', drives=all_drives, companies=all_companies)


@admin_bp.route('/announcements', methods=['GET', 'POST'])
@admin_required
def announcements():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        message = request.form.get('message', '').strip()
        category = request.form.get('category', 'Drive Alert')
        priority = request.form.get('priority', 'Normal')
        target = request.form.get('target_department', 'All Departments')

        ann = Announcement(
            title=title,
            message=message,
            category=category,
            priority=priority,
            target_department=target
        )
        db.session.add(ann)
        db.session.commit()
        flash('Official announcement broadcasted successfully!', 'success')
        return redirect(url_for('admin.announcements'))

    all_announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=all_announcements)


@admin_bp.route('/reports')
@admin_required
def reports():
    total_students = StudentProfile.query.count()
    placed_students = StudentProfile.query.filter_by(placement_status='Placed').count()
    
    # Department breakdown
    depts = db.session.query(StudentProfile.department).distinct().all()
    dept_stats = []
    for (d,) in depts:
        tot = StudentProfile.query.filter_by(department=d).count()
        pl = StudentProfile.query.filter_by(department=d, placement_status='Placed').count()
        pct = round((pl / tot * 100), 1) if tot > 0 else 0
        dept_stats.append({'dept': d, 'total': tot, 'placed': pl, 'percentage': pct})

    # Tier breakdown
    tier_counts = {
        'Super Dream (15+ LPA)': Company.query.filter_by(tier='Super Dream').count(),
        'Dream (8-15 LPA)': Company.query.filter_by(tier='Dream').count(),
        'Core (5-8 LPA)': Company.query.filter_by(tier='Core').count(),
        'Mass Hiring (<5 LPA)': Company.query.filter_by(tier='Mass Hiring').count()
    }

    return render_template(
        'admin/reports.html',
        total_students=total_students,
        placed_students=placed_students,
        placement_rate=round((placed_students / total_students * 100), 1) if total_students > 0 else 0,
        dept_stats=dept_stats,
        tier_counts=tier_counts
    )
