from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, StudentProfile, Company

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('auth/login.html', email=email)

        if not user.is_active:
            flash('Your account has been deactivated. Please contact the Placement Cell.', 'error')
            return render_template('auth/login.html')

        # Store in session
        session['user_id'] = user.id
        session['role'] = user.role
        session['user_name'] = user.full_name
        session['user_email'] = user.email

        flash(f'Welcome back, {user.full_name}!', 'success')

        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'recruiter':
            return redirect(url_for('recruiter.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role', 'student')
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not email or not password or not full_name:
            flash('Please fill in all required fields.', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists. Please log in.', 'error')
            return redirect(url_for('auth.login'))

        # Create user
        user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # If student, create profile
        if role == 'student':
            roll_number = request.form.get('roll_number', '').strip().upper()
            department = request.form.get('department', 'Computer Science & Engineering')
            batch_year = int(request.form.get('batch_year', 2026))
            cgpa = float(request.form.get('cgpa', 8.0))
            tenth = float(request.form.get('tenth_percentage', 85.0))
            twelfth = float(request.form.get('twelfth_percentage', 85.0))
            backlogs = int(request.form.get('active_backlogs', 0))
            skills = request.form.get('skills', 'Python, SQL, HTML, CSS, JavaScript')

            # Check duplicate roll
            if roll_number and StudentProfile.query.filter_by(roll_number=roll_number).first():
                db.session.rollback()
                flash('A student with this Roll Number is already registered.', 'error')
                return render_template('auth/register.html')

            profile = StudentProfile(
                user_id=user.id,
                roll_number=roll_number or f"2022CS{user.id:04d}",
                department=department,
                batch_year=batch_year,
                cgpa=cgpa,
                tenth_percentage=tenth,
                twelfth_percentage=twelfth,
                active_backlogs=backlogs,
                skills=skills
            )
            db.session.add(profile)

        elif role == 'recruiter':
            company_name = request.form.get('company_name', '').strip()
            industry = request.form.get('industry', 'Information Technology')
            tier = request.form.get('tier', 'Dream')

            if company_name:
                company = Company.query.filter_by(name=company_name).first()
                if not company:
                    code = ''.join([c for c in company_name if c.isalnum()])[:6].upper()
                    company = Company(
                        user_id=user.id,
                        name=company_name,
                        code=code,
                        industry=industry,
                        tier=tier,
                        hr_name=full_name,
                        hr_email=email
                    )
                    db.session.add(company)
                else:
                    company.user_id = user.id

        db.session.commit()
        flash('Registration successful! Please log in with your credentials.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/demo-login/<role>')
def demo_login(role):
    """1-Click quick login for evaluating the system."""
    role = role.lower()
    user = None

    if role == 'student':
        user = User.query.filter_by(role='student').first()
    elif role == 'admin':
        user = User.query.filter_by(role='admin').first()
    elif role == 'recruiter':
        user = User.query.filter_by(role='recruiter').first()

    if not user:
        flash(f'Demo user for role {role} not found.', 'error')
        return redirect(url_for('auth.login'))

    session['user_id'] = user.id
    session['role'] = user.role
    session['user_name'] = user.full_name
    session['user_email'] = user.email

    flash(f'Logged in as Demo {user.role.title()} ({user.full_name})', 'success')

    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user.role == 'recruiter':
        return redirect(url_for('recruiter.dashboard'))
    else:
        return redirect(url_for('student.dashboard'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
