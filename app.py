from flask import Flask, render_template, request, redirect, session, flash ,send_from_directory,url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session and flash messages

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # الحد الأقصى 16MB
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'))  # ربط بالصف
    email = db.Column(db.String(120), unique=True, nullable=True)
    code = db.Column(db.String(20), unique=True)
    type = db.Column(db.String(50), default='student')
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))
    reports = db.relationship('Report', backref='student', lazy=True)


# -----------------------------
# 👨‍👩 Parent Model
# -----------------------------
class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(50), default='parent')
    students = db.relationship('Student', backref='parent', lazy=True)
    code = db.Column(db.String(20), unique=True)


# -----------------------------
# 👨‍🏫 Teacher Model
# -----------------------------
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50), default='teacher')
    email = db.Column(db.String(120), unique=True, nullable=True)
    code = db.Column(db.String(20), unique=True)
    phone = db.Column(db.String(20), nullable=False)
    subjects = db.Column(db.String(200))  # نص مفصول بفواصل


# -----------------------------
# 👨‍💼 Admin Model
# -----------------------------
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), default='admin')
    name = db.Column(db.String(100))
    code = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=False)


# -----------------------------
# 👥 User Model (عام)
# -----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    code = db.Column(db.String(20), unique=True)
    user_type = db.Column(db.String(50))  # student / teacher / parent / admin


# -----------------------------
# 📑 Report Model
# -----------------------------
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    title = db.Column(db.String(200))
    picture = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


# -----------------------------
# 📢 Announcement Model
# -----------------------------
class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    code = db.Column(db.String(20), unique=True)
    content = db.Column(db.Text)
    picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


# -----------------------------
# 🏫 Grade Model
# -----------------------------
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    students = db.relationship('Student', backref='grade', lazy=True)


# -----------------------------
# 📚 Subject Model
# -----------------------------
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    code = db.Column(db.String(20), unique=True)
    # teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))


# -----------------------------
# 📝 Homework Model
# -----------------------------
class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    title = db.Column(db.String(200))
    due_date = db.Column(db.DateTime)
    grade = db.Column(db.String(20))
    pdf_link = db.Column(db.String(200))
    pdf_link = db.Column(db.String(200))
# create add admin already add when start code "admin255" whit sqlit3
def create_admin():
    code = "admin255"
    new_admin = Admin(name="Admin", code=code, email="admin@example.com", phone="123456789")
    user = User(name="Admin", email="admin@example.com", phone="123456789", code=code, user_type="admin")
    existing_admin = Admin.query.filter_by(code=code).first()
    if not existing_admin:
        db.session.add(new_admin)
        db.session.add(user)
        db.session.commit()

def add_grades():
    grades = [
        "Pre-KG", "KG1", "KG2",
        "أولى ابتدائي", "تانية ابتدائي", "تالتة ابتدائي",
        "رابعة ابتدائي", "خامسة ابتدائي", "سادسة ابتدائي",
        "أولى إعدادي", "تانية إعدادي", "تالتة إعدادي"
    ]

    for g in grades:
        if not Grade.query.filter_by(name=g).first():
            new_grade = Grade(name=g)
            db.session.add(new_grade)

    db.session.commit()

# Create tables
with app.app_context():
    db.create_all()
    create_admin()
    add_grades()

# Routes
@app.route("/grade/<int:grade_id>")
def grade_students(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    students = Student.query.filter_by(grade_id=grade.id).all()
    grades = Grade.query.all()
    return render_template(
        "dashboard.html",
        grades=grades,
        students=students,
        selected_grade=grade
    )


@app.route("/announcement_add", methods=["POST"])
def announcement_add():
    try:
        title = request.form["title"]
        content = request.form["content"]
        picture = request.form.get("picture")

        new_announcement = Announcement(title=title, content=content, picture=picture)
        db.session.add(new_announcement)
        db.session.commit()

        flash("✅ تم إضافة الإعلان بنجاح")
    except Exception as e:
        db.session.rollback()
        flash(f"⚠️ خطأ أثناء إضافة الإعلان: {str(e)}")
    return redirect("/dashboard")

@app.route("/")
def home():
    if "user_id" in session:
        user_name = User.query.get(session["user_id"]).name
        user_email = User.query.get(session["user_id"]).email
        user_type = User.query.get(session["user_id"]).user_type
        announcements = Announcement.query.all()
        user = {
            "name": user_name,
            "email": user_email,
            "type": user_type
        }
        return render_template("index.html", current_user=True, user=user, announcements=announcements)
    else:
        return render_template("index.html")

@app.route("/search_user", methods=["GET"])
def search_user():
    name = request.args.get("name")
    user = User.query.filter_by(name=name).first()
    return render_template("search_user.html", user=user)


@app.route("/student/<int:student_id>/reports")
def student_reports(student_id):
    if "user_id" not in session:
        flash("لازم تسجل الدخول الأول")
        return redirect("/login")

    user = User.query.get(session["user_id"])
    student = User.query.get_or_404(student_id)

    # 👨‍👩‍👦 لو ولي أمر، لازم يكون الطالب من أولاده
    if user.type == "parent":
        if student not in user.students:
            flash("غير مسموح تشوف بيانات طالب مش ابنك")
            return redirect("/")

    # 👨‍🎓 لو طالب، يشوف تقاريره هو فقط
    if user.type == "student":
        if student.id != user.id:
            flash("غير مسموح تشوف بيانات طالب آخر")
            return redirect("/")

    # 👨‍🏫 لو مدرس أو أدمن، مسموح يشوف أي تقارير (ممكن تحدد صلاحيات أكتر هنا)
    reports = Report.query.filter_by(student_id=student.id).all()
    return render_template("student_reports.html", student=student, reports=reports)


@app.route("/delete_user", methods=["POST"])
def delete_user():
    try:
        user_type = request.form["type"]
        user_id = request.form["id"]

        if user_type == "student":
            user = Student.query.get(user_id)
        elif user_type == "teacher":
            user = Teacher.query.get(user_id)
        elif user_type == "parent":
            user = Parent.query.get(user_id)
        elif user_type == "admin":
            user = Admin.query.get(user_id)
        else:
            flash("⚠️ نوع المستخدم غير معروف")
            return redirect("/users")

        if user:
            db.session.delete(user)
            db.session.commit()
            flash("✅ تم حذف المستخدم بنجاح")
        else:
            flash("⚠️ المستخدم غير موجود")
    except Exception as e:
        db.session.rollback()
        flash(f"⚠️ خطأ أثناء الحذف: {str(e)}")
    return redirect("/users")



@app.route("/login")
def login():
    return render_template("login.html")
@app.route("/log", methods=["GET", "POST"])
def log():
    if request.method == "POST":
        code = request.form["code"]
        user = User.query.filter_by(code=code).first()
    if user:
        session["user_id"] = user.id
        session["role"] = user.user_type
        return redirect("/")
    else:
        flash("الكود غير صحيح ❌")
        return redirect("/login")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    
    # المستخدم الحالي
    current_user = User.query.get(session["user_id"])
    
    students = Student.query.all()
    teachers = Teacher.query.all()
    admins = Admin.query.all()
    subjects = Subject.query.all()
    parents = Parent.query.all()
    reports = Report.query.all()
    announcements = Announcement.query.all()
    all_users = User.query.all()
    homeworks = Homework.query.all()
    grades = Grade.query.all()
    return render_template(
        "dashboard.html",
        user=current_user,
        students=students,
        teachers=teachers,
        admins=admins,
        parents=parents,
        reports=reports,
        subjects=subjects,
        announcements=announcements,
        all_users=all_users,
        homeworks=homeworks,
        grades=grades,
        type=current_user.user_type
    )



@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.")
    return redirect("/login")

@app.route("/users")
def users():
    #for admin only
    if "user_id" not in session or session["role"] != "admin":
        flash("غير مسموح لك بالدخول لهذه الصفحة.")
        return redirect("/")
    all_grades = Grade.query.all()
    all_users = User.query.all()
    all_students = Student.query.all()
    all_teachers = Teacher.query.all()
    all_parents = Parent.query.all()
    all_admins = Admin.query.all()
    return render_template("users.html", users=all_users, students=all_students, teachers=all_teachers, parents=all_parents, 
                           admins=all_admins,subjects=Subject.query.all(), grades=all_grades)

@app.route("/add_user", methods=["POST"])
def add_user():
    try:
        name = request.form["name"]
        type_ = request.form["type"]
        email = request.form.get("email")
        phone = request.form.get("phone")
        code = request.form.get("code")

        # إنشاء مستخدم عام
        user = User(name=name, email=email, phone=phone, code=code, user_type=type_)
        db.session.add(user)
        db.session.commit()

        if type_ == "student":
            grade_id = request.form.get("grade")
            student = Student(name=name, grade_id=grade_id, email=email, code=code)
            db.session.add(student)

        elif type_ == "teacher":
            subject = request.form.get("subject")
            teacher = Teacher(name=name, email=email, phone=phone, code=code, subjects=subject)
            db.session.add(teacher)

        elif type_ == "parent":
            children = request.form.getlist("student_id")
            parent = Parent(
                name=name, email=email, phone=phone, code=code,
                students=[Student.query.get(int(cid)) for cid in children if Student.query.get(int(cid))]
            )
            db.session.add(parent)

        elif type_ == "admin":
            admin = Admin(name=name, email=email, phone=phone, code=code)
            db.session.add(admin)

        db.session.commit()
        flash("✅ تمت إضافة المستخدم بنجاح")
    except Exception as e:
        db.session.rollback()
        flash(f"⚠️ خطأ أثناء إضافة المستخدم: {str(e)}")
    return redirect("/users")

@app.route("/add_subject", methods=["POST"])
def add_subject():
    name = request.form["name"]
    code = request.form["code"]
    subject = Subject(name=name, code=code)
    db.session.add(subject)
    db.session.commit()
    flash("تمت إضافة المادة بنجاح")
    return redirect("/users")

@app.route("/report_add", methods=["POST"])
def report_add():
    student_id = request.form["student_id"]
    title = request.form["title"]
    content = request.form["content"]

    # نعمل التقرير
    new_report = Report(student_id=student_id, title=title, content=content)
    db.session.add(new_report)
    db.session.commit()

    flash("تم إضافة التقرير بنجاح ✅")
    return redirect("/dashboard")

@app.route("/edit_student/<int:id>", methods=["POST"])
def edit_student(id):
    data = request.get_json()
    student = Student.query.get_or_404(id)
    student.name = data.get("name")
    student.grade = data.get("grade")
    student.email = data.get("email")
    student.code = data.get("code")
    student.parent_id = data.get("parent_id") or None
    db.session.commit()
    return {"success": True}

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/announcements")
def announcements():
    all_announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template("announcements.html", announcements=all_announcements)
from werkzeug.utils import secure_filename
from datetime import datetime

# السماح فقط بامتداد PDF
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 📌 راوت إضافة واجب منزلي
@app.route("/homework_add", methods=["POST"])
def homework_add():
    subject_id = request.form["subject_id"]
    title = request.form["title"]
    grade = request.form["grade"]
    due_date = request.form["due_date"]

    # التحقق من رفع ملف
    if "pdf_link" not in request.files:
        flash("❌ لم يتم رفع ملف PDF")
        return redirect("/dashboard")

    file = request.files["pdf_link"]
    if file.filename == "":
        flash("❌ لم يتم اختيار أي ملف")
        return redirect("/dashboard")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], "homework")
        os.makedirs(save_path, exist_ok=True)  # لو المجلد مش موجود يتعمل
        file_path = os.path.join(save_path, filename)
        file.save(file_path)

        # نحفظ في قاعدة البيانات
        new_homework = Homework(
            subject_id=subject_id,
            title=title,
            grade=grade,
            due_date=datetime.strptime(due_date, "%Y-%m-%d"),
            pdf_link=f"/uploads/homework/{filename}"
        )
        db.session.add(new_homework)
        db.session.commit()

        flash("✅ تم إضافة الواجب بنجاح")
    else:
        flash("❌ الملف لازم يكون PDF")

    return redirect("/dashboard")


# 📌 عشان السيرفر يقدر يجيب الملفات المرفوعة
@app.route('/uploads/homework/<filename>')
def uploaded_homework(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], "homework"), filename)


if __name__ == "__main__":
    app.run(debug=True, port=10000)
