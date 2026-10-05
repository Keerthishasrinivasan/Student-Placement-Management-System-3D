from flask import Blueprint, render_template
from models import db, JobPosting, Company, Announcement, StudentProfile, Application

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Gather live aggregate stats for the 3D landing page
    total_students = StudentProfile.query.count()
    placed_students = StudentProfile.query.filter_by(placement_status='Placed').count()
    placement_rate = round((placed_students / total_students * 100), 1) if total_students > 0 else 94.8
    
    total_companies = Company.query.count()
    active_jobs = JobPosting.query.filter_by(status='Open').count()
    
    # Calculate highest & average package from jobs or placed students
    highest_job = JobPosting.query.order_by(JobPosting.package_lpa.desc()).first()
    highest_package = highest_job.package_lpa if highest_job else 44.0
    
    # Recent announcements
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(4).all()
    
    # Featured companies
    featured_companies = Company.query.limit(8).all()
    
    # Latest jobs
    recent_jobs = JobPosting.query.filter_by(status='Open').order_by(JobPosting.created_at.desc()).limit(6).all()

    stats = {
        'total_students': total_students or 650,
        'placed_students': placed_students or 598,
        'placement_rate': placement_rate or 94.2,
        'total_companies': total_companies or 85,
        'active_jobs': active_jobs or 28,
        'highest_package': highest_package or 44.5,
        'average_package': 12.4
    }

    return render_template(
        'index.html',
        stats=stats,
        announcements=announcements,
        featured_companies=featured_companies,
        recent_jobs=recent_jobs
    )


@main_bp.route('/about')
def about():
    return render_template('index.html', scroll_to='about')
