import json
from PIL import Image

global capture, rec_frame, grey, switch, neg, face, rec, out
capture = 0
grey = 0
neg = 0
face = 0
switch = 1
rec = 0

from flask import Flask, flash, request, redirect, render_template, url_for, Response, jsonify
from werkzeug.utils import secure_filename
from flask_paginate import Pagination, get_page_args
from Recognition import recognize_cv2
import cv2
import sqlite3 as sql
import time
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel, db, login
import os
from datetime import datetime
from facenet_pytorch import MTCNN
from genpdf import pdfONSearch
mtcnn = MTCNN(prewhiten=False, keep_all=True, thresholds=[0.6, 0.7, 0.9])
global tempstudent
tempstudent = None
UPLOAD_FOLDER = "C:\\Users\\Srabon\\PycharmProjects\\varsity\\uploaded"
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'gif', 'png'}
STATIC_IMAGE = "C:\\Users\\Srabon\\PycharmProjects\\varsity\\static\\admin"
STUDENT_IMAGE = "C:\\Users\\Srabon\\PycharmProjects\\varsity\\static\\students"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOADED_PHOTOS_DEST'] = STATIC_IMAGE
app.config['UPLOADED_PHOTOS_DEST'] = STUDENT_IMAGE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FRAS3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "b_5#y2LF4Q8znxec"
db.init_app(app)
login.init_app(app)
login.login_view = 'login'
global daily_data
daily_data = None


############################################JINJA##############
def jinja_strlist_to_intlist(ching):
    x = ching
    z = []
    for i in x:
        if not i == "'" and not i == "[" and not i == " " and not i == "]" and not i == ",":
            z.append(i)
    id = []
    for i in range(len(z)):
        id.append((z[i]))
    xs = list(''.join(id))
    dx = ("".join(xs))
    str = dx
    n = 7
    chunks = [str[i:i + n] for i in range(0, len(str), n)]
    ids = [int(i) for i in chunks]
    return ids


# # # make shots directory to save pics
# # try:
# #     os.mkdir('./shots')
# # except OSError as error:
# #     pass
# #

###########################LOGIN######################################

@app.before_first_request
def create_table():
    db.create_all()


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email=email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        phone = request.form['phone']
        file = request.files['image']
        password = request.form['password']

        if UserModel.query.filter_by(email=email).first():
            return ('Email already Present')
        if file.filename == '':
            return redirect(url_for('login'))
        if file and allowed_file(file.filename):
            filename = phone + ".jpg"
            file_loc = os.path.join(STATIC_IMAGE, filename)
            file.save(file_loc)

            user = UserModel(email=email, username=username, phone=phone, image=filename)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
    return render_template('register.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')


#########################LOGIN END###################################################################
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/dashboard')
@login_required
def index():
    return render_template("dashboard.html")


@app.route('/train')
def train():
    return render_template("animate.html")


@app.route('/initiate')
def run_script():
    from Training import startTraining
    startTraining()
    return redirect(url_for('index'))


@app.route('/home')
@login_required
def viewstudent():
    connection = sql.connect("FRASD1test.db")
    connection.row_factory = sql.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Student_Info ORDER BY student_id")
    users = cursor.fetchall()
    return render_template('index.html', users=users)


@app.route('/home/deleterecord/', methods=["GET"])
@login_required
def students():
    if request.method == "GET":
        connection = sql.connect("FRASD1test.db")
        connection.row_factory = sql.Row
        cursor = connection.cursor()
        cursor.execute("select * from Student_Info ORDER BY student_id")
        rows = cursor.fetchall()
        return render_template("students.html", rows=rows)


@app.route('/home/updaterecord/', methods=["GET"])
@login_required
def update():
    if request.method == "GET":
        connection = sql.connect("FRASD1test.db")
        connection.row_factory = sql.Row
        cursor = connection.cursor()
        cursor.execute("select * from Student_Info ORDER BY student_id")
        rows = cursor.fetchall()
        return render_template("update_student.html", rows=rows)


@app.route("/home/updaterecord/<int:id>", methods=["GET", "POST"])
@login_required
def update_record(id):
    if request.method == "GET":
        id = id
        with sql.connect("FRASD1test.db") as connection:

            cursor = connection.cursor()
            cursor.execute("select * from Student_Info where id=?", (id,))
            rows = cursor.fetchall()
            if rows:
                return render_template('update_record.html', rows=rows)
            else:
                flash("Couldn't find")
                return redirect(url_for('index'))


@app.route("/update", methods=["GET", "POST"])
@login_required
def update_student():
    if request.method == "POST":
        try:
            id = request.form['id']
            student_id = request.form["s_id"]
            name = request.form["s_name"]
            email = request.form["s_email"]
            sex = request.form["sex"]
            contact = request.form["s_contact"]
            dob = request.form["dob"]
            file = request.files['image']
            address = request.form["address"]
            if file.filename == '':
                return redirect(url_for('update_student'))
            if file and allowed_file(file.filename):
                import random
                import string
                # printing uppercase
                letters = string.ascii_uppercase
                filename = (''.join(random.choice(letters) for i in range(10)) + '.jpg')
                file_loc = os.path.join(STUDENT_IMAGE, filename)
                file.save(file_loc)

                with sql.connect("FRASD1test.db") as connection:
                    cursor = connection.cursor()
                    updated_record = (student_id, name, email, sex, contact, dob, filename, address, id)
                    print(updated_record)
                    cursor.execute(
                        "UPDATE Student_Info SET student_id =?, name=?, email=?, sex=?, contact=?, dob=?, image=?, address=?  WHERE id=? ",
                        updated_record)

                    connection.commit()
                    flash("Student Update successfully ", 'success')

        except:
            connection.rollback()
            flash("Sorry ! operation interrupted by server", 'warning')
            return redirect(url_for('update_record'))
        finally:
            return redirect(url_for('index'))
            connection.close()


@app.route("/download_attendance")
@login_required
def download():
    return render_template("download.html")


@app.route('/download_data', methods=["POST", "GET"])
@login_required
def download_attendance_data():
    global daily_data
    if request.method == "POST":
        course = request.form['course']
        fdate = request.form["fdate"]
        tdate = request.form["tdate"]
        print(course, fdate, tdate)
        daily_data = {
            "course": course,
            "fdate": fdate,
            "tdate": tdate
        }
        connection = sql.connect("FRASD1test.db")
        connection.row_factory = sql.Row
        cursor = connection.cursor()
        coms = (course, fdate, tdate)

        cursor.execute("SELECT * FROM Attendance WHERE course = ? AND date BETWEEN ? AND ?", coms)
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append([x for x in row])  # or simply data.append(list(row))
        print(data)
        # headers = {'Content-Type': 'application/json'}
        return render_template("datad.html", rows=rows)
    else:
        return render_template('download.html')

        ##################################Health report#################################


@app.route('/health', methods=['GET'])
def health():
    return render_template("report.html")


@app.route('/report', methods=['POST'])
def health_report():
    if request.method == "POST":
        try:
            course = request.form['course']
            s_id = request.form['student_id']
            print(course, s_id)
            with sql.connect("FRASD1test.db") as connection:
                cursor = connection.cursor()
                qdata = (course,)
                qdata2 = (course, s_id)
                cursor.execute("select count(date) from Attendance where course=?", qdata)
                rows = cursor.fetchall()
                total_class = rows[0][0]
                print(total_class)
                cursor.execute("select count(date) from Attendance where course=? and student_id=?", qdata2)
                rows = cursor.fetchall()
                student_present = rows[0][0]
                print(student_present)

                total_percentage = (student_present / total_class) * 100

        except ZeroDivisionError:
            flash("Sorry ! Check again", 'warning')
        except:
            connection.rollback()
            flash("Sorry ! operation interrupted by server", 'warning')
        finally:
            return render_template('performance.html', total_class=total_class, total_percentage=total_percentage,
                                   student_present=student_present)
            connection.close()


@app.route('/download_data/convert', methods=["POST", "GET"])
def convert():
    if request.method == "POST":
        teacher = request.form['tname']
        print(daily_data['fdate'],daily_data['tdate'],daily_data['course'])
        course = daily_data['course']
        fromdate = daily_data['fdate']
        todate = daily_data['tdate']
        return pdfONSearch(fromdate=fromdate, todate=todate, course=course, teacher=teacher)



    else:
        return render_template("download.html")


###############ADD STUDENT #############################


@app.route("/add_student")
@login_required
def add_student():
    return render_template("add_student.html")


@app.route("/saverecord", methods=["POST", "GET"])
@login_required
def saveRecord():
    try:
        if request.method == "POST":
            student_id = request.form["s_id"]
            name = request.form["s_name"]
            email = request.form["s_email"]
            sex = request.form["sex"]
            contact = request.form["s_contact"]
            dob = request.form["dob"]
            address = request.form["address"]
            file = request.files['image']
            tempstudent = {"student_id": student_id,
                           "name": name,
                           "email": email,
                           "sex": sex,
                           "contact": contact,
                           "dob": dob,
                           "address": address,
                           "image": file}
            print(tempstudent)
            if file.filename == '':
                return redirect(url_for('add_student'))
            if file and allowed_file(file.filename):
                import random
                import string
                # printing uppercase
                letters = string.ascii_uppercase
                filename = (''.join(random.choice(letters) for i in range(10)) + '.jpg')
                file_loc = os.path.join(STUDENT_IMAGE, filename)
                file.save(file_loc)
                with sql.connect("FRASD1test.db") as connection:
                    cursor = connection.cursor()
                    connection.execute(
                        "CREATE TABLE IF NOT EXISTS Student_Info (id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER UNIQUE NOT NULL, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, sex TEXT NOT NULL, contact TEXT UNIQUE NOT NULL, dob TEXT NOT NULL, image TEXT NOT NULL, address TEXT NOT NULL )")
                    cursor.execute(
                        "INSERT into Student_Info (student_id, name, email, sex, contact, dob, image , address) values (?,?,?,?,?,?,?,?)",
                        (student_id, name, email, sex, contact, dob, filename, address))
                    connection.commit()
                    flash("Student added successfully ", 'success')
    except:
        connection.rollback()
        flash("Sorry ! operation interrupted by server", 'warning')
        return redirect(url_for('add_student'))
    finally:
        return redirect(url_for('index'))
        connection.close()


@app.route("/home/deleterecord/<int:student_id>", methods=["GET", "POST"])
@login_required
def deleterecord(student_id):
    if request.method == "GET":
        id = student_id
        print(id)
        with sql.connect("FRASD1test.db") as connection:

            cursor = connection.cursor()
            cursor.execute("select * from Student_Info where student_id=?", (id,))
            rows = cursor.fetchall()
            if not rows == []:
                cursor.execute("delete from Student_Info where student_id = ?", (id,))
                flash("Student successfully removed from the list", 'danger')
                return redirect(url_for('index'))

            else:
                flash("Couldn't Delete", 'danger')
                return redirect(url_for('index'))

###################################################################################################################
# @app.route('/dataset',methods=["POST",'GET'])
# def dataset():
#     return render_template('dataset.html')
#
#
# @app.route('/dataset/requests', methods=['POST', 'GET'])
# def tasks():
#     if request.method == 'POST':
#         if request.form.get('click') == 'Capture':
#             camera = cv2.VideoCapture(0)
#             dir = request.form['dir']
#             print(dir)
#             try:
#                 os.mkdir(f'./datasets/{dir}')
#             except OSError as error:
#                 pass
#             if dir:
#                 cv2.namedWindow("test")
#
#                 img_counter = 0
#
#                 while True:
#                     ret, frame = camera.read()
#                     if not ret:
#                         print("failed to grab frame")
#                         break
#                     cv2.imshow("test", frame)
#
#                     k = cv2.waitKey(1)
#                     if k % 256 == 27:
#                         # ESC pressed
#                         print("Escape hit, closing...")
#                         break
#                     elif k % 256 == 32:
#                         for i in range(30):
#                             # SPACE pressed
#                             now = datetime.now()
#                             p = os.path.sep.join([f'./datasets/{dir}', "set{}.jpg".format(str(now).replace(":", ''))])
#                             cv2.imwrite(p, frame)
#                             print("{} written!".format(p))
#                             img_counter += 1
#
#                 camera.release()
#
#                 cv2.destroyAllWindows()
#
#
#
#
#
#     elif request.method == 'GET':
#         return render_template('dataset.html')
#     return render_template('dataset.html')

# ##########CAMERA FILE @########

def gen_frames():  # generate frame by frame from camera
    global capture, rec_frame, tempstudent, switch
    name = str(tempstudent['student_id'])
    DATASET_PATH = os.path.join("datasets", name)
    if not os.path.isdir(DATASET_PATH):
        os.mkdir(DATASET_PATH)
    image_no = 0
    count = 0
    while True:
        success, frame = camera.read()
        if success:
            if (capture):
                count += 1

                faces, _ = mtcnn.detect(Image.fromarray(frame))
                if faces is not None and count % 7 == 0:
                    image_no += 1
                    cv2.imwrite(os.path.join(DATASET_PATH, f"{name}_{image_no}.jpg"), frame)
                    if image_no == 50:
                        break
                image_text = f"Number of image taken {image_no} for {name}"
                frame = cv2.putText(cv2.flip(frame, 1), image_text, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (0, 0, 255), 1)
                frame = cv2.flip(frame, 1)

                if faces is not None:
                    for (x, y, w, h) in faces:
                        x, y, w, h = int(x), int(y), int(w), int(h)
                        cv2.rectangle(frame, (x, y), (w, h), (200, 100, 0), 2)

            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass

        else:
            pass


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/dataset/')
def dataset():
    return render_template('index2.html')


@app.route('/dataset/requests/', methods=['POST', 'GET'])
def tasks():
    global switch, camera
    camera = cv2.VideoCapture(0)
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture = 1

        elif request.form.get('stop') == 'Stop/Start':

            if (switch == 1):
                switch = 0
                camera.release()
                cv2.destroyAllWindows()

            else:
                camera = cv2.VideoCapture(0)
                switch = 1


    elif request.method == 'GET':
        return render_template('index2.html')
    return render_template('index2.html')


if __name__ == '__main__':
    app.run(debug=True)

# tested on 6/7/2021
# now all i need is a flask good interface
# you havent traied any data yet just me and haasan

# run abal .py for test
# can get an id of a student from a particular uploaded image
