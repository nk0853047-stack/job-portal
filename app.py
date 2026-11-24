from flask import Flask, render_template, request, redirect, url_for, flash, session,send_from_directory
import sqlite3
import os
import webbrowser
import threading

app = Flask(__name__)
app.secret_key = "Job-Portal-secret"

DB = "database.db"
UPLOAD_FOLDER = "uploads/resumes"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/recruiter/resume/<path:filename>")
def view_resume(filename):

    if session.get("role", "").lower() != "recruiter":
        return redirect(url_for("login"))

    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=False
    )

# =========================================================
# JOB DATA
# =========================================================

JOBS = [

    (
        1,
        "Frontend Developer",
        "TechNova Labs",
        "Remote",
        "₹35,000/month",
        "Full Time",
        "B.Tech,BCA,BSC.IT",
        "HTML, CSS, JavaScript"
    ),

    (
        2,
        "Python Developer",
        "CodeCraft",
        "Bengaluru",
        "₹45,000/month",
        "Full Time",
        "B.Tech,BCA,BSC.IT",
        "Python, Flask, SQL"
    ),

    (
        3,
        "UI/UX Designer",
        "PixelWorks",
        "Remote",
        "₹40,000/month",
        "Full Time",
        "B.Tech,BCA,BSC.IT",
        "Figma, UI Design"
    ),

    (
        4,
        "Data Analyst",
        "InsightHub",
        "Delhi",
        "₹50,000/month",
        "Full Time",
        "B.Tech,BCA,BSC.IT",
        "Python, Excel, SQL"
    ),

    (
        5,
        "Digital Marketing Executive",
        "GrowSphere",
        "Mumbai",
        "₹30,000/month",
        "Full Time",
        "B.Tech,BCA,BSC.IT",
        "SEO, Social Media"
    ),

    (
        6,
        "GIS Developer",
        "GeoVision",
        "Hyderabad",
        "₹48,000/month",
        "Full Time",
        "B.Tech,BCA,BSC.IT",
        "GIS, JavaScript, Python"
    ),

    (
        7,
        "Backend Developer",
        "InnovateTech",
        "Pune",
        "₹55,000/month",
        "Full Time",
        "B.Tech,BCA,BSC.IT",
        "Python, Node.js, MySQL"
    ),

    (
        8,
        "Java Developer",
        "SoftSolutions",
        "Noida",
        "₹52,000/month",
        "Full Time",
        "B.Tech,BCA,BSC.IT",
        "Java, Spring Boot, SQL"
    )

]


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    # USERS TABLE
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    # PROFILES TABLE
    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            phone TEXT,
            education TEXT,
            skills TEXT,
            location TEXT,
            bio TEXT,
            resume TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    # APPLICATIONS TABLE
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            name TEXT,
            email TEXT,
            resume TEXT
        )
    """)
    # Add qualification columns if they don't exist
    columns = [
       row["name"]
      for row in conn.execute("PRAGMA table_info(profiles)").fetchall()
    ]

    if "tenth" not in columns:
     conn.execute("ALTER TABLE profiles ADD COLUMN tenth TEXT")

    if "twelfth" not in columns:
      conn.execute("ALTER TABLE profiles ADD COLUMN twelfth TEXT")

    if "graduation" not in columns:
      conn.execute("ALTER TABLE profiles ADD COLUMN graduation TEXT")

    conn.commit()
    conn.close()
@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db()

    if request.method == "POST":

        phone = request.form.get("phone", "").strip()
        tenth = request.form.get("tenth", "").strip()
        twelfth = request.form.get("twelfth", "").strip()
        graduation = request.form.get("graduation", "").strip()
        skills = request.form.get("skills", "").strip()
        location = request.form.get("location", "").strip()
        bio = request.form.get("bio", "").strip()

        try:
            existing = conn.execute(
                "SELECT * FROM profiles WHERE user_id = ?",
                (user_id,)
            ).fetchone()

            if existing:
                conn.execute("""
                    UPDATE profiles
                    SET phone = ?,
                        tenth = ?,
                        twelfth = ?,
                        graduation = ?,
                        skills = ?,
                        location = ?,
                        bio = ?
                    WHERE user_id = ?
                """, (
                    phone,
                    tenth,
                    twelfth,
                    graduation,
                    skills,
                    location,
                    bio,
                    user_id
                ))

            else:
                conn.execute("""
                    INSERT INTO profiles
                    (user_id, phone, tenth, twelfth, graduation,
                     skills, location, bio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    phone,
                    tenth,
                    twelfth,
                    graduation,
                    skills,
                    location,
                    bio
                ))

            conn.commit()

            flash("Profile updated successfully!")

        except Exception as e:
            conn.rollback()
            print("PROFILE SAVE ERROR:", e)
            flash("Profile could not be saved. Please try again.")

        finally:
            conn.close()

        return redirect(url_for("profile"))

    profile_data = conn.execute(
        "SELECT * FROM profiles WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    conn.close()
    user_id = session["user_id"]

    conn = get_db()

    user = conn.execute(
      "SELECT name, email FROM users WHERE id = ?",
      (user_id,)
    ).fetchone()

    return render_template(
        "profile.html",
        profile=profile_data
    )

# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        jobs=JOBS
    )

@app.route("/recruiter/applications")
def recruiter_applications():

    if session.get("role", "").lower() != "recruiter":
        return redirect(url_for("login"))

    conn = get_db()

    applications = conn.execute(
        "SELECT * FROM applications ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "applications.html",
        applications=applications
    )
@app.route("/recruiter/shortlist/<int:application_id>", methods=["POST"])
def shortlist_candidate(application_id):

    if session.get("role", "").lower() != "recruiter":
        return redirect(url_for("login"))

    conn = get_db()

    application = conn.execute(
        "SELECT * FROM applications WHERE id = ?",
        (application_id,)
    ).fetchone()

    if not application:
        conn.close()
        flash("Application not found.")
        return redirect(url_for("recruiter_applications"))

    columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(applications)"
        ).fetchall()
    ]

    if "status" not in columns:
        conn.execute(
            "ALTER TABLE applications ADD COLUMN status TEXT DEFAULT 'Pending'"
        )

    conn.execute(
        "UPDATE applications SET status = 'Shortlisted' WHERE id = ?",
        (application_id,)
    )

    conn.commit()
    conn.close()

    flash("Candidate shortlisted successfully!")

    return redirect(url_for("recruiter_shortlisted"))
# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        conn = get_db()

        existing_user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            conn.close()
            flash("Email already registered. Please login.")
            return redirect(url_for("login"))

        conn.execute("""
            INSERT INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            password,
            role
        ))

        conn.commit()
        conn.close()

        flash("Registration successful! Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")
# ================================
# LOGIN PROCESS
# ================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        role = request.form.get("role")
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()

        user = conn.execute(
            """
            SELECT * FROM users
            WHERE email = ? AND password = ? AND role = ?
            """,
            (email, password, role)
        ).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            if role == "candidate":
                return redirect(url_for("candidate_dashboard"))

            elif role == "Recruiter":
                return redirect(url_for("Recruiter_dashboard"))

        flash("Invalid Email or Password")
        return redirect(url_for("login"))

    return render_template("login.html")
    # -----------------------------------------------------
    # CANDIDATE LOGIN
    # -----------------------------------------------------

    if role == "candidate":

        if (email, password) == candidate_account:

            session["role"] = "candidate"

            session["email"] = email

            return redirect(
                url_for("candidate_dashboard")
            )


    # -----------------------------------------------------
    # JOB OWNER / RECRUITER LOGIN
    # -----------------------------------------------------

    if role == "Recruiter":

        if (email, password) == Recruiter_account:

            session["role"] = "Recruiter"

            session["email"] = email

            return redirect(
                url_for("Recruiter_dashboard")
            )


    # -----------------------------------------------------
    # INVALID LOGIN
    # -----------------------------------------------------

    flash("Invalid Email or Password")

    return redirect(
        url_for("login")
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# CANDIDATE DASHBOARD
# =========================================================
@app.route("/candidate")
def candidate_dashboard():

    if session.get("role", "").lower() != "candidate":
        return redirect(url_for("login"))

    conn = get_db()

    try:
        profile = conn.execute(
            "SELECT graduation, skills FROM profiles WHERE user_id = ?",
            (session.get("user_id"),)
        ).fetchone()

        graduation = ""
        candidate_skills = ""

        if profile:
            graduation = (
                profile["graduation"] or ""
            ).strip()

            candidate_skills = (
                profile["skills"] or ""
            ).strip()

        all_jobs = conn.execute(
            "SELECT * FROM jobs ORDER BY id DESC"
        ).fetchall()

        recommended_jobs = []

        qualification = graduation.lower()

        candidate_skill_list = [
            skill.strip().lower()
            for skill in candidate_skills.split(",")
            if skill.strip()
        ]

        for job in all_jobs:

            required_qualification = (
                (job["qualification"] if "qualification" in job.keys() else "Any Graduate")
            ).strip().lower()

            job_skills = (
                job["skills"] or ""
            ).lower()

            # Match qualification
            qualification_match = (
                required_qualification == "any graduate"
                or (
                    qualification
                    and required_qualification in qualification
                )
            )

            # Match candidate skills
            skills_match = any(
                skill in job_skills
                for skill in candidate_skill_list
            )

            if qualification_match or skills_match:
                recommended_jobs.append(job)

        return render_template(
            "candidate.html",
            email=session.get("email"),
            jobs=recommended_jobs,
            qualification=graduation
        )

    finally:
        conn.close()
# =========================================================
# OWNER / RECRUITER DASHBOARD
# =========================================================

@app.route("/Recruiter")
def Recruiter_dashboard():

    if session.get("role") != "Recruiter":

        return redirect(
            url_for("login")
        )


    conn = get_db()


    applications = conn.execute(

        """
        SELECT *
        FROM applications
        ORDER BY id DESC
        """

    ).fetchall()


    conn.close()


    return render_template(

        "owner.html",

        email=session.get("email"),

        jobs=JOBS,

        applications=applications

    )


@app.route("/manage-portal")
def manage_portal():

    if session.get("role", "").lower() != "recruiter":
        return redirect(url_for("login"))

    conn = get_db()

    applications = conn.execute("""
        SELECT *
        FROM applications
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "manage_portal.html",
        applications=applications
    )


# ACTIVE OPPORTUNITIES
@app.route("/recruiter/active-jobs")
def active_jobs():
    if session.get("role") != "Recruiter":
        return redirect(url_for("login"))

    conn = get_db()
    jobs = conn.execute(
        "SELECT * FROM jobs ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template(
        "active_jobs.html",
        jobs=jobs
    )

@app.route("/recruiter/toggle-job/<int:job_id>", methods=["POST"])
def toggle_job_status(job_id):

    if session.get("role", "").lower() != "recruiter":
        return redirect(url_for("login"))

    conn = get_db()

    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(jobs)").fetchall()
    ]

    if "status" not in columns:
        conn.execute("""
            ALTER TABLE jobs
            ADD COLUMN status TEXT DEFAULT 'Active'
        """)

    job = conn.execute(
        "SELECT * FROM jobs WHERE id = ?",
        (job_id,)
    ).fetchone()

    if job:
        current_status = job["status"] or "Active"

        new_status = (
            "Inactive"
            if current_status.lower() == "active"
            else "Active"
        )

        conn.execute(
            "UPDATE jobs SET status = ? WHERE id = ?",
            (new_status, job_id)
        )

        conn.commit()

    conn.close()

    return redirect(url_for("active_jobs"))
# APPLICATIONS PAGE
@app.route("/recruiter/applications")
def applications():
    if session.get("role") != "Recruiter":
        return redirect(url_for("login"))

    conn = get_db()
    applications = conn.execute(
        "SELECT * FROM applications ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template(
        "applications.html",
        applications=applications
    )

# SHORTLISTED CANDIDATES
@app.route("/recruiter/shortlisted")
def recruiter_shortlisted():

    if session.get("role", "").lower() != "recruiter":
        return redirect(url_for("login"))

    conn = get_db()

    # Check whether status column exists
    columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(applications)"
        ).fetchall()
    ]

    # Add status column if it doesn't exist
    if "status" not in columns:
        conn.execute("""
            ALTER TABLE applications
            ADD COLUMN status TEXT DEFAULT 'Pending'
        """)
        conn.commit()

    # Fetch only shortlisted candidates
    shortlisted_apps = conn.execute("""
        SELECT *
        FROM applications
        WHERE status = 'Shortlisted'
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "shortlisted.html",
        applications=shortlisted_apps
    )

@app.route(
    "/recruiter/update-status/<int:application_id>/<status>",
    methods=["POST", "GET"]
)
@app.route(
    "/recruiter/update-status/<int:application_id>",
    methods=["POST"]
)
def update_candidate_status(application_id, status=None):

    if session.get("role", "").lower() != "recruiter":
        return redirect(url_for("login"))

    # Status URL se ya form se lena
    if status is None:
        status = request.form.get("status")

    allowed_statuses = ["Shortlisted", "Selected", "Rejected"]

    if status not in allowed_statuses:
        flash("Invalid candidate status!", "error")
        return redirect(url_for("recruiter_applications"))

    conn = get_db()

    try:
        columns = [
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(applications)"
            ).fetchall()
        ]

        if "status" not in columns:
            conn.execute("""
                ALTER TABLE applications
                ADD COLUMN status TEXT DEFAULT 'Pending'
            """)

        conn.execute("""
            UPDATE applications
            SET status = ?
            WHERE id = ?
        """, (status, application_id))

        conn.commit()

        flash(
            f"Candidate status updated to {status} successfully!",
            "success"
        )

    except Exception as e:
        conn.rollback()
        print("Status update error:", e)
        flash("Unable to update candidate status.", "error")

    finally:
        conn.close()

    return redirect(url_for("recruiter_applications"))


@app.route("/recruiter/selected")
def selected_candidates():

    if session.get("role", "").lower() != "recruiter":
        return redirect(url_for("login"))

    conn = get_db()

    candidates = conn.execute("""
        SELECT * FROM applications
        WHERE status = 'Selected'
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "selected.html",
        candidates=candidates
    )

@app.route("/recruiter/rejected")
def rejected_candidates():

    if session.get("role", "").lower() != "recruiter":
        return redirect(url_for("login"))

    conn = get_db()

    candidates = conn.execute("""
        SELECT * FROM applications
        WHERE status = 'Rejected'
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "rejected.html",
        candidates=candidates
    )    
# =========================================================
# SEARCH JOBS
# =========================================================

@app.route("/jobs")
def jobs():

    search = request.args.get(
        "q",
        ""
    ).lower()


    location = request.args.get(
        "location",
        ""
    ).lower()


    filtered_jobs = []


    for job in JOBS:

        title = job[1].lower()

        company = job[2].lower()

        job_location = job[3].lower()

        skills = job[6].lower()


        # -------------------------------------------------
        # SEARCH BY JOB TITLE / COMPANY / SKILLS
        # -------------------------------------------------

        if search:

            if (
                search not in title
                and search not in company
                and search not in skills
            ):

                continue


        # -------------------------------------------------
        # SEARCH BY LOCATION
        # -------------------------------------------------

        if location:

            if location not in job_location:

                continue


        filtered_jobs.append(job)


    return render_template(

        "jobs.html",

        jobs=filtered_jobs,

        q=search,

        location=location

    )
# DELETE JOB
@app.route('/recruiter/delete-job/<int:job_id>', methods=['POST'])
def delete_job(job_id):

    if session.get('role', '').lower() != 'recruiter':
        return redirect(url_for('login'))

    conn = get_db()

    try:
        conn.execute(
            'DELETE FROM jobs WHERE id = ?',
            (job_id,)
        )
        conn.commit()

        flash('Job deleted successfully!', 'success')

    except Exception:
        conn.rollback()
        flash('Unable to delete job.', 'error')

    finally:
        conn.close()

    return redirect(url_for('active_jobs'))

# =========================================================
# JOB DETAILS
# =========================================================

@app.route("/job/<int:job_id>")
def job_details(job_id):

    job = None


    for item in JOBS:

        if item[0] == job_id:

            job = item

            break


    if job is None:

        return "Job not found", 404


    return render_template(

        "job-details.html",

        job=job

    )


# =========================================================
# APPLY FOR JOB
# =========================================================

@app.route("/apply/<int:job_id>", methods=["GET", "POST"])
def apply(job_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "candidate":
        return redirect(url_for("login"))

    conn = None

    try:
        conn = get_db()

        # Find job in database instead of JOBS list
        job = conn.execute(
            "SELECT * FROM jobs WHERE id = ?",
            (job_id,)
        ).fetchone()

        if job is None:
            return "Job not found in database", 404

        if request.method == "POST":

            name = request.form.get("name", "").strip()
            email = session.get("email", "").strip()

            resume = request.files.get("resume")
            filename = ""

            if not name or not email:
                flash("Please enter your name and email.", "error")
                return redirect(url_for("apply", job_id=job_id))

            # Check duplicate application
            existing = conn.execute(
                """
                SELECT id FROM applications
                WHERE job_id = ? AND email = ?
                """,
                (job_id, email)
            ).fetchone()

            if existing:
                flash("You have already applied for this job!", "error")
                return redirect(url_for("apply", job_id=job_id))

            # Upload resume
            if resume and resume.filename:
                filename = os.path.basename(resume.filename)

                os.makedirs(UPLOAD_FOLDER, exist_ok=True)

                resume.save(
                    os.path.join(UPLOAD_FOLDER, filename)
                )

            # Save application in database
            conn.execute(
                """
                INSERT INTO applications
                (job_id, name, email, resume)
                VALUES (?, ?, ?, ?)
                """,
                (job_id, name, email, filename)
            )

            conn.commit()

            flash(
                "Job Application submitted successfully!",
                "success"
            )

            return redirect(url_for("apply", job_id=job_id))

        return render_template(
            "apply.html",
            job=job,
            email=session.get("email")
        )

    except Exception as e:
        print("APPLICATION ERROR:", e)
        flash("Application could not be submitted. Please try again.", "error")
        return redirect(url_for("dashboard"))

    finally:
        if conn is not None:
            conn.close()

# =========================================================
# DASHBOARD REDIRECT
# =========================================================

@app.route("/dashboard")
def dashboard():

    role = session.get("role")


    if role == "candidate":

        return redirect(

            url_for(
                "candidate_dashboard"
            )

        )


    if role == "Recruiter":

        return redirect(

            url_for(
                "Recruiter_dashboard"
            )

        )


    return redirect(

        url_for("login")

    )


# =========================================================
# RECRUITER / OWNER JOB MANAGEMENT
# =========================================================

@app.route("/recruiter")
def recruiter():
    if session.get("role") != "Recruiter":
        return redirect(url_for("login"))

    return redirect(url_for("Recruiter_dashboard"))


# RECRUITER PROFILE / JOB POSTING PAGE
@app.route("/recruiter/profile")
def recruiter_profile():

    if session.get("role") != "Recruiter":
        return redirect(url_for("login"))

    return render_template("recruiter_profile.html")

# POST JOB
@app.route('/post-job', methods=['POST'])
def post_job():

    if session.get('role', '').lower() != 'recruiter':
        return redirect(url_for('login'))

    title = request.form.get('title', '').strip()
    company = request.form.get('company', '').strip()
    location = request.form.get('location', '').strip()
    salary = request.form.get('salary', '').strip()
    duration = request.form.get('duration', '').strip()
    skills = request.form.get('skills', '').strip()
    qualification = request.form.get(
        'qualification', 'Any Graduate'
    ).strip()

    start_date = request.form.get('start_date') or None
    deadline = request.form.get('deadline') or None

    if not title or not company or not location:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('recruiter_profile'))

    conn = get_db()

    try:
        # Check existing jobs table columns
        columns = [
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(jobs)"
            ).fetchall()
        ]

        if not columns:
            raise Exception("Jobs table does not exist in this database.")

        # Add missing columns
        if "qualification" not in columns:
            conn.execute("""
                ALTER TABLE jobs
                ADD COLUMN qualification TEXT DEFAULT 'Any Graduate'
            """)

        if "start_date" not in columns:
            conn.execute("""
                ALTER TABLE jobs
                ADD COLUMN start_date TEXT
            """)

        if "deadline" not in columns:
            conn.execute("""
                ALTER TABLE jobs
                ADD COLUMN deadline TEXT
            """)

        # Insert job into database
        conn.execute("""
            INSERT INTO jobs (
                title,
                company,
                location,
                salary,
                duration,
                skills,
                qualification,
                start_date,
                deadline
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            company,
            location,
            salary,
            duration,
            skills,
            qualification,
            start_date,
            deadline
        ))

        conn.commit()

        print("JOB POST SUCCESS: Job saved successfully!")

        flash('🎉 Job Published Successfully!', 'success')

    except Exception as e:
        conn.rollback()

        print("JOB POST ERROR:", repr(e))

        flash(
            '❌ Job could not be published. Please try again.',
            'error'
        )

    finally:
        conn.close()

    return redirect(url_for('recruiter_profile'))
# =========================================================
# RUN APPLICATION
# =========================================================
    
if __name__ == "__main__":

    init_db()

    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
