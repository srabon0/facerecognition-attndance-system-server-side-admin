
import sqlite3 as sql
from datetime import datetime
with sql.connect("FRASD.db") as connection:
    try:
      cursor = connection.cursor()
      times = datetime.now()
      # date = times.strftime("%Y-%m-%d")
      date = "08/22/2021"
      cursor.execute("select Student_info.student_id,name, status,course from Attendance INNER JOIN Student_Info on Student_Info.student_id = Attendance.student_id Where date =? ;",(date,))
      result =  cursor.fetchall()
      # course = result[0][2]
      print(result)
    except Exception as e:
      print(e)
    finally:
        cursor.close()