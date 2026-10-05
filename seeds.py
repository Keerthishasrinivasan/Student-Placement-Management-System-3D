from datetime import datetime, timedelta
from app import create_app
from models import db, User, StudentProfile, Company, JobPosting, Application, PlacementDrive, Announcement, MockAssessment, AssessmentQuestion, AssessmentResult

def seed_database():
    app = create_app()
    with app.app_context():
        # Drop and recreate tables cleanly
        db.drop_all()
        db.create_all()
        print("Database tables initialized.")

        # ==========================================
        # 1. ADMIN USER
        # ==========================================
        admin = User(
            email='placement.director@university.edu',
            full_name='Dr. K. S. Ramanathan',
            role='admin',
            phone='+91 98401 23456',
            avatar_color='#6366f1'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)

        # ==========================================
        # 2. RECRUITERS & COMPANIES
        # ==========================================
        recruiter_google = User(
            email='campus.hire@google.com',
            full_name='Sarah Jenkins',
            role='recruiter',
            phone='+91 98765 43210',
            avatar_color='#ea4335'
        )
        recruiter_google.set_password('Recruiter@123')
        db.session.add(recruiter_google)

        recruiter_ms = User(
            email='campus@microsoft.com',
            full_name='David Miller',
            role='recruiter',
            phone='+91 98765 11223',
            avatar_color='#00a4ef'
        )
        recruiter_ms.set_password('Recruiter@123')
        db.session.add(recruiter_ms)

        recruiter_cisco = User(
            email='university@cisco.com',
            full_name='Aarav Mehta',
            role='recruiter',
            phone='+91 98765 99887',
            avatar_color='#049fd9'
        )
        recruiter_cisco.set_password('Recruiter@123')
        db.session.add(recruiter_cisco)

        db.session.flush()

        # Companies
        c_google = Company(
            user_id=recruiter_google.id,
            name='Google',
            code='GOOGL',
            industry='Cloud, AI & Software Engineering',
            website='https://careers.google.com',
            logo_url='https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg',
            description='Google is an American multinational technology company focusing on artificial intelligence, online advertising, search engine technology, cloud computing, and computer software.',
            tier='Super Dream',
            location='Bengaluru / Hyderabad',
            hr_name='Sarah Jenkins',
            hr_email='campus.hire@google.com',
            rating=4.9
        )
        c_ms = Company(
            user_id=recruiter_ms.id,
            name='Microsoft',
            code='MSFT',
            industry='Software & Cloud Systems',
            website='https://careers.microsoft.com',
            logo_url='https://upload.wikimedia.org/wikipedia/commons/9/96/Microsoft_logo_%282012%29.svg',
            description='Microsoft Corporation is an American multinational technology corporation producing computer software, consumer electronics, personal computers, and related services.',
            tier='Super Dream',
            location='Bengaluru / Noida / Hyderabad',
            hr_name='David Miller',
            hr_email='campus@microsoft.com',
            rating=4.8
        )
        c_amazon = Company(
            name='Amazon',
            code='AMZN',
            industry='E-Commerce, Cloud (AWS) & AI',
            website='https://amazon.jobs',
            description='Amazon is guided by four principles: customer obsession rather than competitor focus, passion for invention, commitment to operational excellence, and long-term thinking.',
            tier='Super Dream',
            location='Bengaluru / Chennai / Hyderabad',
            hr_name='Rohan Verma',
            hr_email='university-hire@amazon.com',
            rating=4.7
        )
        c_cisco = Company(
            user_id=recruiter_cisco.id,
            name='Cisco Systems',
            code='CSCO',
            industry='Networking, Security & Cloud',
            website='https://cisco.com/careers',
            description='Cisco enables people to make powerful connections--whether in business, education, philanthropy, or creativity. Hardware, software, and service offerings.',
            tier='Dream',
            location='Bengaluru',
            hr_name='Aarav Mehta',
            hr_email='university@cisco.com',
            rating=4.6
        )
        c_deloitte = Company(
            name='Deloitte USI',
            code='DLTE',
            industry='Technology Consulting & Analytics',
            website='https://deloitte.com/careers',
            description='Deloitte drives progress through digital transformation, analytics, cyber risk advisory, and cloud modernizations for Fortune 500 enterprises.',
            tier='Dream',
            location='Hyderabad / Bengaluru',
            hr_name='Neha Kapoor',
            hr_email='recruiting@deloitte.com',
            rating=4.5
        )
        c_tcs = Company(
            name='Tata Consultancy Services',
            code='TCS',
            industry='IT Services & Consulting',
            website='https://tcs.com/careers',
            description='A purposeful mind and innovated technology can solve any problem. TCS delivers cutting-edge digital enterprise transformations worldwide.',
            tier='Core',
            location='Pan-India / Remote',
            hr_name='Vikram Seth',
            hr_email='campus@tcs.com',
            rating=4.3
        )

        db.session.add_all([c_google, c_ms, c_amazon, c_cisco, c_deloitte, c_tcs])
        db.session.flush()

        # ==========================================
        # 3. JOB POSTINGS
        # ==========================================
        now = datetime.utcnow()

        j_google_sde = JobPosting(
            company_id=c_google.id,
            title='Software Engineer - Campus Graduate',
            job_type='Full Time',
            package_lpa=44.5,
            stipend_pm=110000,
            location='Bengaluru / Hyderabad',
            min_cgpa=8.0,
            max_backlogs=0,
            eligible_departments='Computer Science, Information Technology, Electronics & Communication',
            skills_required='Python, C++, Java, Data Structures, Algorithms, System Design, SQL',
            description='As a Software Development Engineer at Google, you will tackle some of the most complex computing problems in distributed systems, machine learning, and high-performance algorithms.',
            responsibilities='• Write scalable, robust, and clean code in Python/C++/Java.\n• Build resilient microservices and APIs.\n• Collaborate with cross-functional teams in agile iterations.\n• Optimize latency and throughput for global scale systems.',
            selection_process='Round 1: Online Coding Challenge (LeetCode Medium-Hard)\nRound 2: Technical Interview 1 (DSA & Problem Solving)\nRound 3: Technical Interview 2 (System Design & Code Quality)\nRound 4: Googliness & Leadership Discussion',
            deadline=now + timedelta(days=20),
            drive_date=now + timedelta(days=25),
            status='Open'
        )

        j_ms_sde = JobPosting(
            company_id=c_ms.id,
            title='Software Engineer (Azure & Cloud)',
            job_type='Full Time',
            package_lpa=42.0,
            stipend_pm=95000,
            location='Bengaluru / Noida',
            min_cgpa=7.5,
            max_backlogs=0,
            eligible_departments='Computer Science, Information Technology, Electronics & Communication',
            skills_required='Data Structures, Algorithms, C++, Python, SQL, Operating Systems, Cloud',
            description='Join Microsoft to empower every person and every organization on the planet to achieve more. Work on Azure cloud infrastructure, AI models, and enterprise software.',
            responsibilities='• Architect cloud native services on Azure.\n• Diagnose, reproduce, and resolve critical performance bottlenecks.\n• Practice automated testing and CI/CD best practices.',
            selection_process='1. Cognitive & Coding Assessment\n2. Technical Round 1: DSA & OOPS\n3. Technical Round 2: OS, Networks, Database Internals\n4. Techno-Managerial Round',
            deadline=now + timedelta(days=15),
            drive_date=now + timedelta(days=22),
            status='Open'
        )

        j_amazon_sde = JobPosting(
            company_id=c_amazon.id,
            title='Software Development Engineer I (SDE-1)',
            job_type='Full Time',
            package_lpa=38.0,
            stipend_pm=85000,
            location='Bengaluru / Hyderabad / Chennai',
            min_cgpa=7.5,
            max_backlogs=0,
            eligible_departments='Computer Science, Information Technology',
            skills_required='Python, Java, OOP, Data Structures, SQL, Problem Solving',
            description='Amazon is hiring enthusiastic SDE-1 candidates for AWS, Retail Platform, and Prime Video engineering teams.',
            responsibilities='• Design modular, extensible back-end components.\n• Build low-latency services with 99.99% availability.\n• Participate in code reviews and operational reviews.',
            selection_process='1. Amazon Online Assessment (OAA 1 & 2)\n2. 3 Virtual Technical Bar Raiser Interviews',
            deadline=now + timedelta(days=18),
            drive_date=now + timedelta(days=24),
            status='Open'
        )

        j_cisco_net = JobPosting(
            company_id=c_cisco.id,
            title='Software & Network Platform Engineer',
            job_type='Full Time',
            package_lpa=18.5,
            stipend_pm=65000,
            location='Bengaluru',
            min_cgpa=7.0,
            max_backlogs=0,
            eligible_departments='Computer Science, Information Technology, Electronics & Communication, Electrical',
            skills_required='Python, Computer Networks, Linux, SQL, REST APIs, Git',
            description='Work on next-generation networking protocols, software-defined networks, telemetry, and cybersecurity platforms at Cisco.',
            responsibilities='• Implement network automation tools in Python.\n• Analyze TCP/IP, BGP, and SDN protocols.\n• Design automated test suites for continuous verification.',
            selection_process='1. Online MCQ & Coding Assessment\n2. Technical Round: Networks, Python, DSA\n3. Managerial & HR Round',
            deadline=now + timedelta(days=12),
            drive_date=now + timedelta(days=19),
            status='Open'
        )

        j_deloitte_analyst = JobPosting(
            company_id=c_deloitte.id,
            title='Technology Consulting Analyst',
            job_type='Full Time',
            package_lpa=12.0,
            stipend_pm=40000,
            location='Hyderabad / Bengaluru',
            min_cgpa=6.8,
            max_backlogs=1,
            eligible_departments='All Departments',
            skills_required='SQL, Python, Data Analytics, Communication, Problem Solving',
            description='Help global enterprise clients solve critical business challenges through technology integration, data intelligence, and cloud engineering.',
            responsibilities='• Translate business requirements into technical blueprints.\n• Build SQL queries, reporting dashboards, and ETL pipelines.\n• Present findings to senior leadership.',
            selection_process='1. Aptitude & Verbal Ability Test\n2. Case Study Evaluation\n3. Partner Interview',
            deadline=now + timedelta(days=25),
            drive_date=now + timedelta(days=30),
            status='Open'
        )

        j_tcs_digital = JobPosting(
            company_id=c_tcs.id,
            title='Digital / Prime Innovator Cadre',
            job_type='Full Time',
            package_lpa=9.0,
            stipend_pm=30000,
            location='Pan-India',
            min_cgpa=6.5,
            max_backlogs=1,
            eligible_departments='All Departments',
            skills_required='Python, SQL, HTML, CSS, JavaScript, Basic OOPS',
            description='TCS Digital Cadre for high-performing engineering students with strong programming foundations and analytical reasoning.',
            responsibilities='• Develop digital enterprise modules.\n• Work on modern cloud frameworks and REST APIs.',
            selection_process='1. National Qualifier Test (NQT Digital)\n2. Technical & HR Interview',
            deadline=now + timedelta(days=30),
            drive_date=now + timedelta(days=35),
            status='Open'
        )

        db.session.add_all([j_google_sde, j_ms_sde, j_amazon_sde, j_cisco_net, j_deloitte_analyst, j_tcs_digital])
        db.session.flush()

        # ==========================================
        # 4. STUDENTS & PROFILES
        # ==========================================
        # Student 1: Arun Kumar (CSE, Placed at Google!)
        u_arun = User(
            email='arun.cse@university.edu',
            full_name='Arun Kumar',
            role='student',
            phone='+91 99441 12233',
            avatar_color='#10b981'
        )
        u_arun.set_password('Student@123')
        db.session.add(u_arun)
        db.session.flush()

        p_arun = StudentProfile(
            user_id=u_arun.id,
            roll_number='2022CS0101',
            department='Computer Science & Engineering',
            batch_year=2026,
            cgpa=9.35,
            tenth_percentage=94.5,
            twelfth_percentage=95.0,
            active_backlogs=0,
            history_of_backlogs=0,
            skills='Python, C++, Data Structures, Algorithms, SQL, Flask, React, Docker, System Design, Git',
            placement_status='Placed',
            dream_company='Google',
            preferred_role='Software Development Engineer',
            github_url='https://github.com/arun-kumar-dev',
            linkedin_url='https://linkedin.com/in/arun-kumar-cs',
            bio='Competitive programmer (5-star CodeChef, LeetCode 2150+) passionate about scalable backend architectures and AI systems.'
        )
        db.session.add(p_arun)

        # Student 2: Priya Sharma (IT, In Process)
        u_priya = User(
            email='priya.it@university.edu',
            full_name='Priya Sharma',
            role='student',
            phone='+91 98840 22334',
            avatar_color='#8b5cf6'
        )
        u_priya.set_password('Student@123')
        db.session.add(u_priya)
        db.session.flush()

        p_priya = StudentProfile(
            user_id=u_priya.id,
            roll_number='2022IT0142',
            department='Information Technology',
            batch_year=2026,
            cgpa=8.82,
            tenth_percentage=91.0,
            twelfth_percentage=92.5,
            active_backlogs=0,
            skills='Java, Python, Spring Boot, SQL, AWS, Algorithms, REST APIs, HTML, CSS',
            placement_status='In Process',
            dream_company='Microsoft',
            preferred_role='Cloud & Backend Engineer',
            github_url='https://github.com/priyasharma-code',
            linkedin_url='https://linkedin.com/in/priya-sharma-it',
            bio='Full-stack developer with experience in microservices, distributed caching, and cloud deployments.'
        )
        db.session.add(p_priya)

        # Student 3: Karthik Rajan (ECE, In Process)
        u_karthik = User(
            email='karthik.ece@university.edu',
            full_name='Karthik Rajan',
            role='student',
            phone='+91 97722 33445',
            avatar_color='#f59e0b'
        )
        u_karthik.set_password('Student@123')
        db.session.add(u_karthik)
        db.session.flush()

        p_karthik = StudentProfile(
            user_id=u_karthik.id,
            roll_number='2022EC0210',
            department='Electronics & Communication Engineering',
            batch_year=2026,
            cgpa=8.45,
            tenth_percentage=89.0,
            twelfth_percentage=88.5,
            active_backlogs=0,
            skills='Python, C++, Computer Networks, SQL, Linux, Git, Embedded Systems, IoT',
            placement_status='In Process',
            dream_company='Cisco Systems',
            preferred_role='Network Platform Engineer',
            github_url='https://github.com/karthik-rajan-ece',
            linkedin_url='https://linkedin.com/in/karthik-rajan-ece',
            bio='Bridging hardware communications and cloud networking through automation scripts and protocol analysis.'
        )
        db.session.add(p_karthik)

        # Student 4: Ananya Sengupta (CSE, Unplaced / Seeking)
        u_ananya = User(
            email='ananya.cse@university.edu',
            full_name='Ananya Sengupta',
            role='student',
            phone='+91 96633 44556',
            avatar_color='#06b6d4'
        )
        u_ananya.set_password('Student@123')
        db.session.add(u_ananya)
        db.session.flush()

        p_ananya = StudentProfile(
            user_id=u_ananya.id,
            roll_number='2022CS0305',
            department='Computer Science & Engineering',
            batch_year=2026,
            cgpa=7.92,
            tenth_percentage=86.0,
            twelfth_percentage=84.5,
            active_backlogs=0,
            skills='Python, HTML, CSS, JavaScript, SQL, Flask, Git, Data Analysis',
            placement_status='Unplaced',
            dream_company='Deloitte USI',
            preferred_role='Technology Consulting Analyst',
            github_url='https://github.com/ananya-sengupta',
            linkedin_url='https://linkedin.com/in/ananya-sengupta',
            bio='Enthusiastic web engineer building human-centric applications and analyzing data-driven workflows.'
        )
        db.session.add(p_ananya)

        db.session.flush()

        # ==========================================
        # 5. APPLICATIONS & PIPELINE STAGES
        # ==========================================
        # Arun Kumar: Offered & Accepted Google (44.5 LPA)
        app_arun_google = Application(
            job_id=j_google_sde.id,
            student_id=p_arun.id,
            applied_date=now - timedelta(days=20),
            status='Offered',
            current_round_index=6,
            interview_date=now - timedelta(days=3),
            interview_link='https://meet.google.com/xyz-placement-final',
            recruiter_notes='Outstanding performance in dynamic programming and system design rounds. Highly recommended.',
            candidate_feedback='Clear explanation of tree traversal trade-offs and clean production-ready code.',
            offered_package_lpa=44.5,
            match_percentage=96
        )

        # Priya Sharma: Technical Interview at Microsoft (42.0 LPA)
        app_priya_ms = Application(
            job_id=j_ms_sde.id,
            student_id=p_priya.id,
            applied_date=now - timedelta(days=10),
            status='Technical Interview',
            current_round_index=4,
            interview_date=now + timedelta(days=2, hours=4),
            interview_link='https://teams.microsoft.com/l/meetup-join/msft-campus-round-2',
            recruiter_notes='Cleared cognitive & coding test with 95 percentile score. Scheduled for Technical Round 2.',
            match_percentage=89
        )

        # Priya Sharma: Shortlisted at Amazon (38.0 LPA)
        app_priya_amazon = Application(
            job_id=j_amazon_sde.id,
            student_id=p_priya.id,
            applied_date=now - timedelta(days=5),
            status='Shortlisted',
            current_round_index=2,
            interview_date=now + timedelta(days=6),
            interview_link='https://chime.aws/interview-session-402',
            recruiter_notes='Profile screened and cleared academic criteria. Online assessment invitation sent.',
            match_percentage=85
        )

        # Karthik Rajan: HR Interview at Cisco (18.5 LPA)
        app_karthik_cisco = Application(
            job_id=j_cisco_net.id,
            student_id=p_karthik.id,
            applied_date=now - timedelta(days=12),
            status='HR Interview',
            current_round_index=5,
            interview_date=now + timedelta(days=1, hours=2),
            interview_link='https://cisco.webex.com/meet/campus-hr-interview',
            recruiter_notes='Strong foundation in networking protocols and Python scripting. Final managerial discussion.',
            match_percentage=92
        )

        # Ananya: Applied to Deloitte (12.0 LPA)
        app_ananya_deloitte = Application(
            job_id=j_deloitte_analyst.id,
            student_id=p_ananya.id,
            applied_date=now - timedelta(days=3),
            status='Aptitude Test',
            current_round_index=3,
            interview_date=now + timedelta(days=4),
            interview_link='https://deloitte.zoom.us/j/campus-aptitude-slot-1',
            recruiter_notes='Aptitude portal credentials dispatched to student email.',
            match_percentage=82
        )

        # Ananya: Applied to TCS Digital (9.0 LPA)
        app_ananya_tcs = Application(
            job_id=j_tcs_digital.id,
            student_id=p_ananya.id,
            applied_date=now - timedelta(days=2),
            status='Applied',
            current_round_index=1,
            match_percentage=78
        )

        db.session.add_all([
            app_arun_google,
            app_priya_ms,
            app_priya_amazon,
            app_karthik_cisco,
            app_ananya_deloitte,
            app_ananya_tcs
        ])

        # ==========================================
        # 6. PLACEMENT DRIVES
        # ==========================================
        d1 = PlacementDrive(
            company_id=c_google.id,
            title='Google Annual Campus Recruitment 2026',
            drive_date=now + timedelta(days=25),
            venue='Auditorium A & Virtual CodeSignal Platform',
            mode='Hybrid',
            rounds_summary='Online Coding (CodeSignal) -> 2 Technical Rounds -> Leadership Interview',
            eligibility_summary='CSE/IT/ECE with CGPA >= 8.0 and zero standing backlogs',
            status='Scheduled'
        )

        d2 = PlacementDrive(
            company_id=c_ms.id,
            title='Microsoft University Hiring Drive',
            drive_date=now + timedelta(days=22),
            venue='Microsoft Teams Virtual Platform',
            mode='Virtual',
            rounds_summary='Codility Assessment -> System Design & Algorithms -> Director Round',
            eligibility_summary='Circuit branches with CGPA >= 7.5',
            status='Scheduled'
        )

        d3 = PlacementDrive(
            company_id=c_cisco.id,
            title='Cisco Campus Network & Cloud Challenge',
            drive_date=now + timedelta(days=19),
            venue='Seminar Hall 2 & WebEx',
            mode='Hybrid',
            rounds_summary='Aptitude + CS fundamentals test -> 2 Technical rounds -> HR discussion',
            eligibility_summary='CSE/IT/ECE/EEE with CGPA >= 7.0',
            status='Scheduled'
        )

        db.session.add_all([d1, d2, d3])

        # ==========================================
        # 7. ANNOUNCEMENTS
        # ==========================================
        a1 = Announcement(
            title='URGENT: Microsoft Azure Technical Interviews Scheduled',
            message='Shortlisted candidates for Microsoft Technical Round 2 have received their meeting invites on the portal. Please ensure high-speed internet and quiet environment.',
            category='Interview Schedule',
            priority='Urgent',
            target_department='CSE, IT, ECE'
        )

        a2 = Announcement(
            title='Google Campus Drive Registration Deadline Approaching',
            message='All eligible students (CGPA >= 8.0) must verify their resume link and apply through the portal before the deadline. Late submissions will strictly not be permitted.',
            category='Drive Alert',
            priority='High',
            target_department='All Eligible'
        )

        a3 = Announcement(
            title='Cisco Systems Drive Shortlist Published',
            message='Cisco has released the candidates selected for the final HR round. Check your Applications tab for the interview slot details.',
            category='Shortlist Result',
            priority='Normal',
            target_department='All Departments'
        )

        db.session.add_all([a1, a2, a3])

        # ==========================================
        # 8. MOCK ASSESSMENTS & QUESTIONS
        # ==========================================
        m_apt = MockAssessment(
            title='Quantitative Aptitude & Logical Reasoning Master Test',
            category='Quantitative Aptitude',
            duration_mins=15,
            total_questions=5,
            description='Test your speed and accuracy in probability, time & work, data interpretation, and pattern reasoning for top company entrance rounds.'
        )
        db.session.add(m_apt)
        db.session.flush()

        q_apt1 = AssessmentQuestion(
            assessment_id=m_apt.id,
            question_text='A train 240 m long passes a pole in 24 seconds. How long will it take to pass a platform 650 m long?',
            option_a='65 seconds',
            option_b='89 seconds',
            option_c='100 seconds',
            option_d='75 seconds',
            correct_option='B',
            explanation='Speed of train = 240 / 24 = 10 m/s. Total distance to cross platform = 240 + 650 = 890 m. Time = 890 / 10 = 89 seconds.',
            difficulty='Easy'
        )

        q_apt2 = AssessmentQuestion(
            assessment_id=m_apt.id,
            question_text='A bag contains 4 red, 5 blue, and 6 green balls. Two balls are drawn at random. What is the probability that none of them is red?',
            option_a='11/21',
            option_b='1/3',
            option_c='33/35',
            option_d='11/35',
            correct_option='A',
            explanation='Total balls = 15. Non-red balls = 11. P(both non-red) = (11C2) / (15C2) = (11 * 10 / 2) / (15 * 14 / 2) = 55 / 105 = 11 / 21.',
            difficulty='Medium'
        )

        q_apt3 = AssessmentQuestion(
            assessment_id=m_apt.id,
            question_text='If "P + Q" means P is brother of Q, "P - Q" means P is sister of Q, and "P * Q" means P is father of Q. Which represents that C is nephew of M?',
            option_a='M + K * C',
            option_b='M - K * C + T',
            option_c='C + P * M',
            option_d='K * C - M',
            correct_option='B',
            explanation='M - K means M is sister of K. K * C means K is father of C. C + T means C is male (brother of T). Therefore, C is nephew of M.',
            difficulty='Medium'
        )

        q_apt4 = AssessmentQuestion(
            assessment_id=m_apt.id,
            question_text='A can do a piece of work in 12 days and B in 15 days. They work together for 5 days and then B leaves. How many days will A take to finish the remaining work?',
            option_a='3 days',
            option_b='4 days',
            option_c='2.5 days',
            option_d='5 days',
            correct_option='A',
            explanation='1 day work of (A+B) = 1/12 + 1/15 = 9/60 = 3/20. Work done in 5 days = 5 * (3/20) = 3/4. Remaining work = 1/4. Time taken by A = (1/4) / (1/12) = 3 days.',
            difficulty='Easy'
        )

        q_apt5 = AssessmentQuestion(
            assessment_id=m_apt.id,
            question_text='Find the next term in the sequence: 4, 9, 25, 49, 121, ?',
            option_a='144',
            option_b='169',
            option_c='196',
            option_d='225',
            correct_option='B',
            explanation='The sequence represents squares of consecutive prime numbers: 2^2=4, 3^2=9, 5^2=25, 7^2=49, 11^2=121, 13^2=169.',
            difficulty='Medium'
        )

        db.session.add_all([q_apt1, q_apt2, q_apt3, q_apt4, q_apt5])

        # Technical Quiz
        m_tech = MockAssessment(
            title='Core Computer Science & Data Structures Assessment',
            category='Technical Coding & DSA',
            duration_mins=20,
            total_questions=5,
            description='Test your mastery in time complexity, binary trees, dynamic programming, operating systems, and SQL relational querying.'
        )
        db.session.add(m_tech)
        db.session.flush()

        q_tech1 = AssessmentQuestion(
            assessment_id=m_tech.id,
            question_text='What is the worst-case time complexity of searching an element in a Balanced Binary Search Tree (AVL Tree) containing N nodes?',
            option_a='O(1)',
            option_b='O(N)',
            option_c='O(log N)',
            option_d='O(N log N)',
            correct_option='C',
            explanation='Because an AVL tree guarantees balance with height h <= 1.44 log2(N), the search time complexity in the worst case is strictly O(log N).',
            difficulty='Easy'
        )

        q_tech2 = AssessmentQuestion(
            assessment_id=m_tech.id,
            question_text='In SQL, which clause is evaluated BEFORE the SELECT clause in query execution order?',
            option_a='ORDER BY',
            option_b='LIMIT',
            option_c='WHERE',
            option_d='OFFSET',
            correct_option='C',
            explanation='SQL logical query execution order: 1. FROM 2. WHERE 3. GROUP BY 4. HAVING 5. SELECT 6. DISTINCT 7. ORDER BY 8. LIMIT.',
            difficulty='Medium'
        )

        q_tech3 = AssessmentQuestion(
            assessment_id=m_tech.id,
            question_text='Which scheduling algorithm in Operating Systems can cause the Convoy Effect?',
            option_a='Round Robin (RR)',
            option_b='First-Come, First-Served (FCFS)',
            option_c='Shortest Job First (SJF)',
            option_d='Priority Preemptive',
            correct_option='B',
            explanation='In FCFS, if a CPU-bound process with a huge burst time arrives first, many I/O-bound processes wait behind it, causing the Convoy Effect.',
            difficulty='Medium'
        )

        q_tech4 = AssessmentQuestion(
            assessment_id=m_tech.id,
            question_text='Which Python data structure provides O(1) amortized average time complexity for both insertions and lookups?',
            option_a='List',
            option_b='Tuple',
            option_c='Dict (Hash Table)',
            option_d='Deque searching',
            correct_option='C',
            explanation='Python dictionaries and sets are implemented using hash tables with open addressing, yielding O(1) average lookup and insertion.',
            difficulty='Easy'
        )

        q_tech5 = AssessmentQuestion(
            assessment_id=m_tech.id,
            question_text='What property guarantees that a database transaction is completely saved and persists even across hardware or power crashes?',
            option_a='Atomicity',
            option_b='Consistency',
            option_c='Isolation',
            option_d='Durability',
            correct_option='D',
            explanation='Durability (from ACID) ensures that once a transaction commits, its modifications will not be lost, even during server crashes or power failures (via WAL / logs).',
            difficulty='Easy'
        )

        db.session.add_all([q_tech1, q_tech2, q_tech3, q_tech4, q_tech5])

        # Commit all data
        db.session.commit()
        print("Database populated successfully with realistic placement data!")

if __name__ == '__main__':
    seed_database()
