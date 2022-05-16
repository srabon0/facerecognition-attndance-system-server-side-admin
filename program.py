import json
from PIL import Image
global capture, rec_frame, grey, switch, neg, face, rec, out
capture = 0
grey = 0
neg = 0
face = 0
switch = 0
rec = 0

from flask import Flask, flash, request, redirect,render_template,url_for,Response,jsonify
from werkzeug.utils import secure_filename
from flask_paginate import Pagination, get_page_args
from Recognition import recognize_cv2
import cv2
import sqlite3 as sql
import time
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel,db,login
import os
from datetime import datetime
from facenet_pytorch import MTCNN
# from sqltojs import get_all_users
mtcnn = MTCNN(prewhiten=False, keep_all=True, thresholds=[0.6, 0.7, 0.9])
global tempstudent
tempstudent = {}

UPLOAD_FOLDER = "C:\\Users\\Srabon\\PycharmProjects\\varsity\\uploaded"
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'gif','png'}
STATIC_IMAGE = "C:\\Users\\Srabon\\PycharmProjects\\varsity\\static\\admin"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOADED_PHOTOS_DEST'] = STATIC_IMAGE
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
  x=ching
  z = []
  for i in x:
      if not i =="'" and not i == "[" and not i==" " and not i == "]" and not i== ",":
          z.append(i)
  id = []
  for i in range(len(z)):
      id.append((z[i]))
  xs=list(''.join(id))
  dx = ("".join(xs))
  str = dx
  n = 7
  chunks = [str[i:i+n] for i in range(0, len(str), n)]
  ids = [int(i) for i in chunks]
  return ids
# # make shots directory to save pics
# try:
#     os.mkdir('./shots')
# except OSError as error:
#     pass
#
name = str(input("Person Name: "))
DATASET_PATH = os.path.join("datasets", name)
if not os.path.isdir(DATASET_PATH):
  os.mkdir(DATASET_PATH)
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
            print(file.filename)
            filename = phone +".jpg"
            file_loc = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
            file.save(file_loc)

            user = UserModel(email=email, username=username,phone=phone,image=filename)
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

def get_users(page=1, total=100, per_page=5):
    offset = total - ((page - 1) * per_page) + 1
    con = sql.connect('FRASD.db')
    cur = con.cursor()
    query = '''SELECT *
                FROM Student_Info
                WHERE id < ?
                ORDER BY student_id
                LIMIT ?;'''
    cur.execute(query, (offset, per_page))
    users = cur.fetchall()
    cur.close()
    con.close()
    return users
print(get_users())

@app.route('/home')
@login_required
def index():
    connection = sql.connect("FRASD.db")
    cursor = connection.cursor()
    page, per_page, offset = get_page_args(page_parameter='page',  # I don't use this offset value at all
                                           per_page_parameter='per_page')
    per_page = 5
    cursor.execute("SELECT COUNT(id) FROM Student_Info")
    total = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    pagination_users = get_users(page=page, total=total, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,css_framework='bootstrap4')
    return render_template('dashboard.html',
                           users=pagination_users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination)


@app.route('/home/deleterecord/',methods=["GET"])
@login_required
def students():
    if request.method=="GET":
        connection = sql.connect("FRASD.db")
        connection.row_factory = sql.Row
        cursor = connection.cursor()
        cursor.execute("select * from Student_Info ORDER BY student_id")
        rows = cursor.fetchall()
        return render_template("students.html", rows=rows)


@app.route('/home/updaterecord/',methods=["GET"])
@login_required
def update():
    if request.method == "GET":
        connection = sql.connect("FRASD.db")
        connection.row_factory = sql.Row
        cursor = connection.cursor()
        cursor.execute("select * from Student_Info ORDER BY student_id")
        rows = cursor.fetchall()
        return render_template("update_student.html", rows=rows)

@app.route("/home/updaterecord/<int:id>",methods = ["GET","POST"])
@login_required
def update_record(id):
    if request.method == "GET":
        id = id
        with sql.connect("FRASD.db") as connection:

            cursor = connection.cursor()
            cursor.execute("select * from Student_Info where id=?", (id,))
            rows = cursor.fetchall()
            if rows:
                return render_template('update_record.html',rows=rows)
            else:
                flash("Couldn't find")
                return redirect(url_for('index'))
@app.route("/update",methods = ["GET","POST"])
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
            address = request.form["address"]
            print(student_id,name,email,sex)
            with sql.connect("FRASD.db") as connection:
                cursor = connection.cursor()
                updated_record = (student_id,name,email,sex,contact,dob,address,id)
                cursor.execute("UPDATE Student_Info SET student_id =?, name=?, email=?, sex=?, contact=?, dob=?, address=?  WHERE id=? ",updated_record)
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

@app.route('/download_data',methods=["POST","GET"])
def download_attendance_data():
    global daily_data
    if request.method == "POST":
        course = request.form["course"]

        fdate =  request.form["fdate"]
        tdate =  request.form["tdate"]
        print(tdate)
        print(course)
        print(fdate)
        daily_data = {
            "course" : course,
            "fdate":fdate,
            "tdate": tdate
        }
        connection = sql.connect("FRASD1test.db")
        connection.row_factory = sql.Row
        cursor = connection.cursor()
        coms = (course,fdate,tdate)

        cursor.execute("SELECT * FROM Attendance WHERE course = ? AND date BETWEEN ? AND ?",coms)
        rows = cursor.fetchall()
        data=[]
        for row in rows:
            data.append([x for x in row])  # or simply data.append(list(row))
        print(data)
        #headers = {'Content-Type': 'application/json'}
        # jsondata = get_all_users(True)
        # print(jsondata)



        return render_template("datad.html",rows=rows)
    else:
        return render_template('download.html')


@app.route('/download_data/convert',methods = ["POST","GET"])
def convert():
    if request.method == "POST":
        teacher = request.form['tname']
        from fpdf import FPDF
        fdate = daily_data["fdate"]
        tdate = daily_data["tdate"]
        with sql.connect("FRASD1test.db") as connection:
            try:
                cursor = connection.cursor()
                cursor.execute("select * from Attendance")
                result = cursor.fetchall()
                course = result[0][2]

                pdf = FPDF()
                pdf.add_page()

                page_width = pdf.w - 2 * pdf.l_margin

                pdf.set_font('Times', 'B', 14.0)
                title = f"Attendance report of {course}"
                date = f"from {fdate} to {tdate}"
                pdf.cell(page_width, 0.0, title, align='C')
                pdf.cell(page_width, 0.0, date, align="C")
                pdf.ln(10)

                pdf.set_font('Courier', '', 8)

                col_width = page_width / 4

                pdf.ln(1)

                th = pdf.font_size

                for row in result:
                    pdf.cell(col_width / 8, th, str(row[0]), border=1, align="J")
                    pdf.cell(col_width / 3, th, str(row[1]), border=1, align="J")
                    pdf.cell(col_width, th, row[3], border=1, align="J")
                    pdf.cell(col_width, th, row[4], border=1, align="J")

                    pdf.ln(th)

                pdf.ln(10)

                pdf.set_font('Times', '', 8)
                pdf.cell(page_width,0.0,f"Generated by-:{teacher} ",align="R")
                pdf.cell(page_width, 0.0, '- end of report -', align='C')

                return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                headers={'Content-Disposition': 'attachment;filename=attendancedata.pdf'})
            except Exception as e:
                print(e)
            finally:
                cursor.close()

    else:
        return render_template("download.html")


###############ADD STUDENT #############################



@app.route("/add_student")
@login_required
def add_student():
    return render_template("add_student.html")




@app.route("/saverecord",methods = ["POST","GET"])
@login_required
def saveRecord():

    if request.method == "POST":
        try:
            student_id = request.form["s_id"]
            name = request.form["s_name"]
            email = request.form["s_email"]
            sex = request.form["sex"]
            contact = request.form["s_contact"]
            dob = request.form["dob"]
            address = request.form["address"]
            tempstudent = {"student_id":student_id,
                           "name":name,
                           "email":email,
                           "sex":sex,
                           "contact":contact,
                           "dob":dob,
                           "address":address}
            print(tempstudent)
            with sql.connect("FRASD.db") as connection:
                cursor = connection.cursor()
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS Student_Info (id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER UNIQUE NOT NULL, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, sex TEXT NOT NULL, contact TEXT UNIQUE NOT NULL, dob TEXT NOT NULL, address TEXT NOT NULL )")
                cursor.execute("INSERT into Student_Info (student_id, name, email, sex, contact, dob, address) values (?,?,?,?,?,?,?)",(student_id,name, email, sex, contact, dob, address))
                connection.commit()
                flash("Student added successfully ", 'success')
        except:
            connection.rollback()
            flash("Sorry ! operation interrupted by server", 'warning')
            return redirect(url_for('add_student'))
        finally:
            return redirect(url_for('index'))
            connection.close()


@app.route("/home/deleterecord/<int:student_id>",methods = ["GET","POST"])
@login_required
def deleterecord(student_id):
    if request.method == "GET":
        id = student_id
        print(id)
        with sql.connect("FRASD.db") as connection:

            cursor = connection.cursor()
            cursor.execute("select * from Student_Info where student_id=?", (id,))
            rows = cursor.fetchall()
            if not rows == []:
                cursor.execute("delete from Student_Info where student_id = ?",(id,))
                flash("Student successfully removed from the list",'danger')
                return redirect(url_for('index'))

            else:
                flash("Couldn't Delete",'danger')
                return redirect(url_for('index'))

@app.route('/attendance',methods=["POST","GET"])
def attendance():
    if request.method == "POST":
        stu_id = request.form["student_id"]
        times = datetime.now()
        print(times)
        day = times.strftime("%m/%d/%Y")
        timed = times.strftime("%H:%M:%S")
        print(day,timed)
        print(stu_id)
        int_stu = jinja_strlist_to_intlist(stu_id)
        print(int_stu)
        course = "data commmunication"
        status = None
        with sql.connect("FRASD.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DROP TABLE Attendance")
            cursor.execute("select student_id from Student_info")
            ids = cursor.fetchall()
            print(type(ids[0]))
            out = [item for t in ids for item in t]
            print(out)
            absent_list = list(set(out) - set(int_stu))
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS Attendance (id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER KEY NOT NULL, course TEXT NOT NULL, date TEXT NOT NULL, status TEXT NOT NULL, FOREIGN KEY (student_id) REFERENCES Student_Info(student_id))")
            for stid in out:
                if stid in int_stu:
                    status = "present"
                    cursor.execute(
                                 "INSERT INTO Attendance (student_id, course, date, status) values (?,?,?,?)",(stid, course, day, status,))

            for absid in absent_list:
                status = "absent"
                cursor.execute("INSERT INTO Attendance (student_id, course, date, status) values (?,?,?,?)",(absid, course, day, status,))

            connection.commit()


        # with sql.connect("FRASD.db") as connection:
        #     cursor = connection.cursor()
        #     cursor.execute("CREATE TABLE IF NOT EXISTS Attendance (student_id INTEGER PRIMARY KEY NOT NULL, course TEXT NOT NULL, date TEXT NOT NULL, status TEXT NOT NULL)")
        #     for stuid in int_stu:
        #         cursor.execute(
        #             "INSERT INTO Attendance (student_id, course, date, status) values (?,?,?,?)",(stuid, course, day, status,))
        #
        flash("Attendence successfully Taken ", 'success')

        return redirect('/home')

@app.route("/viewattendance")
def viewattendance():
    connection = sql.connect("FRASD.db")
    connection.row_factory = sql.Row
    cursor = connection.cursor()
    cursor.execute("select * from Attendance ORDER BY student_id")
    rows = cursor.fetchall()
    for row in rows:
        course=row['course'].upper()
    return render_template("attendance.html", rows=rows,course=course)
# ###################################################################################################################
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

##########CAMERA FILE @########


def gen_frames():  # generate frame by frame from camera
    global out, capture, rec_frame
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
                    if image_no == 20:
                        camera.release()
                        cv2.destroyAllWindows()

                        break
                image_text = f"Number of image taken {image_no} for {name}"
                frame = cv2.putText(cv2.flip(frame, 1), image_text, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (0, 0, 255), 4)
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

if __name__=='__main__':
    app.run(debug=True,host="0.0.0.0")


# tested on 6/7/2021
#now all i need is a flask good interface
#you havent traied any data yet just me and haasan

#run abal .py for test
# can get an id of a student from a particular uploaded image
