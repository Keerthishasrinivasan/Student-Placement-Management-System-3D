from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User account model for Students, Recruiters, and Administrators."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'admin', 'recruiter'
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    avatar_color = db.Column(db.String(30), default='#3b82f6')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    company = db.relationship('Company', backref='recruiter_user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class StudentProfile(db.Model):
    """Academic and placement profile for students."""
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    department = db.Column(db.String(80), nullable=False)  # Computer Science, Information Technology, Electronics, etc.
    batch_year = db.Column(db.Integer, nullable=False, default=2026)
    cgpa = db.Column(db.Float, nullable=False, default=8.0)
    tenth_percentage = db.Column(db.Float, nullable=False, default=85.0)
    twelfth_percentage = db.Column(db.Float, nullable=False, default=85.0)
    active_backlogs = db.Column(db.Integer, nullable=False, default=0)
    history_of_backlogs = db.Column(db.Integer, nullable=False, default=0)
    skills = db.Column(db.Text, default='Python, SQL, HTML, CSS, JavaScript')
    resume_file = db.Column(db.String(255), nullable=True)
    github_url = db.Column(db.String(200), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)
    placement_status = db.Column(db.String(30), default='Unplaced')  # 'Unplaced', 'In Process', 'Placed'
    dream_company = db.Column(db.String(100), default='Google')
    preferred_role = db.Column(db.String(100), default='Software Development Engineer')
    bio = db.Column(db.Text, default='Passionate software developer interested in full-stack engineering and cloud systems.')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    assessment_results = db.relationship('AssessmentResult', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def skill_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def __repr__(self):
        return f'<StudentProfile {self.roll_number} - {self.department}>'


class Company(db.Model):
    """Company / Recruiter Organization."""
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    industry = db.Column(db.String(80), nullable=False)
    website = db.Column(db.String(200), nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    tier = db.Column(db.String(30), default='Dream')  # 'Super Dream' (15+ LPA), 'Dream' (8-15 LPA), 'Core' (5-8 LPA), 'Mass' (<5 LPA)
    location = db.Column(db.String(100), default='Bangalore / Remote')
    hr_name = db.Column(db.String(100), nullable=True)
    hr_email = db.Column(db.String(120), nullable=True)
    hr_phone = db.Column(db.String(20), nullable=True)
    rating = db.Column(db.Float, default=4.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    jobs = db.relationship('JobPosting', backref='company', lazy='dynamic', cascade='all, delete-orphan')
    drives = db.relationship('PlacementDrive', backref='company', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Company {self.name} [{self.tier}]>'


class JobPosting(db.Model):
    """Recruitment opportunities posted by companies."""
    __tablename__ = 'job_postings'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    job_type = db.Column(db.String(50), default='Full Time')  # Full Time, Internship, FTE + Internship
    package_lpa = db.Column(db.Float, nullable=False)  # CTC in Lakhs Per Annum
    stipend_pm = db.Column(db.Integer, nullable=True)  # Monthly stipend for internships
    location = db.Column(db.String(100), default='Bengaluru / Hyderabad')
    min_cgpa = db.Column(db.Float, default=7.0)
    max_backlogs = db.Column(db.Integer, default=0)
    eligible_departments = db.Column(db.String(255), default='CSE, IT, ECE')
    skills_required = db.Column(db.Text, default='Python, Data Structures, SQL, Algorithms')
    description = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text, nullable=True)
    selection_process = db.Column(db.Text, default='1. Online Aptitude & Coding Test\n2. Technical Interview 1\n3. Technical Interview 2\n4. HR Discussion')
    deadline = db.Column(db.DateTime, nullable=False)
    drive_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Open')  # 'Open', 'Closed', 'Upcoming'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='job', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def eligible_dept_list(self):
        if not self.eligible_departments:
            return []
        return [d.strip() for d in self.eligible_departments.split(',') if d.strip()]

    @property
    def skill_req_list(self):
        if not self.skills_required:
            return []
        return [s.strip() for s in self.skills_required.split(',') if s.strip()]

    def is_student_eligible(self, student_profile):
        """Check if a student meets all eligibility criteria for this job."""
        if not student_profile:
            return False, "No profile found"
        if student_profile.cgpa < self.min_cgpa:
            return False, f"CGPA requirement not met (Requires {self.min_cgpa}+, your CGPA is {student_profile.cgpa})"
        if student_profile.active_backlogs > self.max_backlogs:
            return False, f"Backlog limit exceeded (Allowed: {self.max_backlogs}, you have {student_profile.active_backlogs})"
        
        dept_match = any(d.lower() in student_profile.department.lower() for d in self.eligible_dept_list)
        if not dept_match and 'All' not in self.eligible_departments:
            return False, f"Department not eligible (Allowed: {self.eligible_departments})"
        
        return True, "Eligible to apply"

    def __repr__(self):
        return f'<JobPosting {self.title} - {self.package_lpa} LPA>'


class Application(db.Model):
    """Student Job Application with multi-round recruitment tracker."""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Recruitment Pipeline Stages:
    # 1: Applied, 2: Shortlisted, 3: Aptitude Round, 4: Technical Interview, 5: HR Interview, 6: Offered, (or Rejected, Accepted, Declined)
    status = db.Column(db.String(40), default='Applied')
    current_round_index = db.Column(db.Integer, default=1)
    
    interview_date = db.Column(db.DateTime, nullable=True)
    interview_link = db.Column(db.String(255), nullable=True)
    recruiter_notes = db.Column(db.Text, nullable=True)
    candidate_feedback = db.Column(db.Text, nullable=True)
    offer_letter_path = db.Column(db.String(255), nullable=True)
    offered_package_lpa = db.Column(db.Float, nullable=True)
    match_percentage = db.Column(db.Integer, default=85)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: One application per student per job
    __table_args__ = (db.UniqueConstraint('job_id', 'student_id', name='uq_job_student_application'),)

    def __repr__(self):
        return f'<Application Job {self.job_id} by Student {self.student_id} [{self.status}]>'


class PlacementDrive(db.Model):
    """Scheduled On-Campus or Virtual Placement Drive."""
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    drive_date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(150), default='Main Auditorium / Virtual Portal')
    mode = db.Column(db.String(30), default='Hybrid')  # 'On-Campus', 'Virtual', 'Hybrid'
    rounds_summary = db.Column(db.Text, default='Pre-Placement Talk -> Online Test -> Technical Interviews -> HR Round')
    eligibility_summary = db.Column(db.String(200), default='CGPA >= 7.5, No standing backlogs, Circuit Branches')
    status = db.Column(db.String(30), default='Scheduled')  # 'Scheduled', 'In Progress', 'Completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PlacementDrive {self.title} on {self.drive_date}>'


class Announcement(db.Model):
    """Official notices and alerts broadcast by Placement Officers."""
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Drive Alert')  # 'Drive Alert', 'Interview Schedule', 'Shortlist', 'General'
    priority = db.Column(db.String(20), default='Normal')  # 'Urgent', 'High', 'Normal'
    target_department = db.Column(db.String(100), default='All Departments')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Announcement {self.title} [{self.priority}]>'


class MockAssessment(db.Model):
    """Pre-Placement Preparation Assessment Module."""
    __tablename__ = 'mock_assessments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'Quantitative Aptitude', 'Technical Coding & DSA', 'Verbal & Reasoning', 'Core CS'
    duration_mins = db.Column(db.Integer, default=15)
    total_questions = db.Column(db.Integer, default=10)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    questions = db.relationship('AssessmentQuestion', backref='assessment', lazy='dynamic', cascade='all, delete-orphan')
    results = db.relationship('AssessmentResult', backref='assessment', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<MockAssessment {self.title}>'


class AssessmentQuestion(db.Model):
    """Questions for placement readiness quizzes."""
    __tablename__ = 'assessment_questions'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('mock_assessments.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(5), nullable=False)  # 'A', 'B', 'C', or 'D'
    explanation = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), default='Medium')

    def __repr__(self):
        return f'<AssessmentQuestion {self.id} for Assessment {self.assessment_id}>'


class AssessmentResult(db.Model):
    """Score records for student practice assessments."""
    __tablename__ = 'assessment_results'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('mock_assessments.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    time_taken_seconds = db.Column(db.Integer, default=300)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AssessmentResult Student {self.student_id} Score: {self.score}/{self.total_marks}>'
