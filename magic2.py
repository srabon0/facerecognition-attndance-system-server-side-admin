import flask
import werkzeug
import time
import os
from datetime import datetime
import sqlite3 as sql
import cv2
from Recognition import recognize_cv2
from fpdf import FPDF
UPLOAD_FOLDER = "C:\\Users\\Srabon\\PycharmProjects\\varsity\\uploaded"

def which_period(time):
    from datetime import datetime
    current_time = datetime.strftime(time, "%H:%M:%S")  # output: 11:12:12
    print(current_time)
    class1 = "10:00:34"
    class1end = "11:59:00"
    class2end = "13:00:00"
    if  class1 < current_time < class1end:
        course = "Data communication "
    elif class1end<current_time<class2end :
        course = "Numerical Methods"
    else:
        course = "Artificial Intelligence"

    return course


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



app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/', methods = ['GET', 'POST'])
def handle_request():
    aq_face = []
    files_ids = list(flask.request.files)
    print("\nNumber of Received Images : ", len(files_ids))
    image_num = 1
    for file_id in files_ids:
        print("\nSaving Image ", str(image_num), "/", len(files_ids))
        imagefile = flask.request.files[file_id]
        filename = werkzeug.utils.secure_filename(imagefile.filename)
        print("Image Filename : " + imagefile.filename)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = timestr +".jpg"
        file_loc = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        imagefile.save(file_loc)
        image_num = image_num + 1
        test = cv2.imread(file_loc)
        faces = recognize_cv2(test)
        print(type(faces))
        for face in faces:
            if (face['top_prediction']['confidence']) > 0.90:
                aq_face.append(face['top_prediction']['label'])

    int_stu = jinja_strlist_to_intlist(aq_face)
    course = which_period(datetime.now())
    status = None
    with sql.connect("FRASD1test.db") as connection:
        cursor = connection.cursor()
        times = datetime.now()
        day = times.strftime("%Y-%m-%d")
        out = [8171003,8171006,8171001,8171002,8171055,8171333,8171013,8171045]
        print(out)
        absent_list = list(set(out) - set(int_stu))
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS Attendance (id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER KEY NOT NULL, course TEXT NOT NULL, date TEXT NOT NULL, status TEXT NOT NULL, FOREIGN KEY (student_id) REFERENCES Student_Info(student_id))")
        for stid in out:
            if stid in int_stu:
                status = "present"
                cursor.execute(
                    "INSERT INTO Attendance (student_id, course, date, status) values (?,?,?,?)",
                    (stid, course, day, status,))

        for absid in absent_list:
            status = "absent"
            cursor.execute("INSERT INTO Attendance (student_id, course, date, status) values (?,?,?,?)",
                           (absid, course, day, status,))

        connection.commit()



    print("\n")
    return "Image(s) Uploaded Successfully. Come Back Soon."

app.run(host="0.0.0.0", port=5000, debug=True)