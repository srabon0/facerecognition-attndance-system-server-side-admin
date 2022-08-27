import json
import time
import sqlite3 as sql
from flask import  Response,jsonify
import random
import string
letters = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
from fpdf import FPDF

TABLE_COL_NAMES = ("SL NO", "Student ID", "Nick Name", "Status")
TABLE_DATA = []

pdf = FPDF()

pdf.add_page()
################################for single day
def pdfReportGEN(date):
    # title = f"Attendance report of { course }"
    #
    # pdf.set_font('Times', 'B', 20.0)
    # present = f"of The Date: {date}"
    # pdf.ln(10)
    # pdf.cell(200, 0.0, title, align='C')
    # pdf.ln(10)
    # pdf.set_font('Times', 'B', 12.0)
    # pdf.cell(200, 0.0, present, align='C')
    # pdf.ln(10)
    #
    # pdf.set_font("Times", size=12)
    #
    # line_height = pdf.font_size * 2
    # col_width = pdf.epw / 4  # distribute content evenly
    with sql.connect("FRASD1test.db") as connection:
        try:
            cursor = connection.cursor()
            date = date
            cursor.execute(
                "select Student_info.student_id,name, status,course from Attendance INNER JOIN Student_Info on Student_Info.student_id = Attendance.student_id Where date =? ;",
                (date,))

            result = cursor.fetchall()
            # print("result is ", result)
            i = 1
            # print(result)
            for item in result:
                strID = str(item[0])
                stdName = str(item[1].split()[0])
                stdStatus = str(item[2])
                # tupdata = (str(i), strID, stdName, stdStatus)
                dictData = {
                    "index": str(i),
                    "studentId": strID,
                    "studentName": stdName,
                    "status": stdStatus
                }

                TABLE_DATA.append(dictData)
                i = i + 1


        except Exception as e:
            print(e)
        finally:
            cursor.close()
            json_object = json.dumps(TABLE_DATA, indent=4)
            print(json_object)
            return  jsonify(json_object)

    # def render_table_header():
    #     pdf.set_font(style="B")  # enabling bold text
    #     for col_name in TABLE_COL_NAMES:
    #         pdf.cell(col_width, line_height, col_name, border=1)
    #     pdf.ln(line_height)
    #     pdf.set_font(style="")  # disabling bold text
    #
    # render_table_header()
    # for _ in range(10):  # repeat data rows
    #     for row in TABLE_DATA:
    #         if pdf.will_page_break(line_height):
    #             render_table_header()
    #         for datum in row:
    #             pdf.cell(col_width, line_height, datum, border=1)
    #         pdf.ln(line_height)
    #
    # pdf.ln(10)
    #
    # pdf.set_font('Times', '', 10.0)
    # pdf.cell(200, 0.0, '- end of report -', align='C')
    # timestr = time.strftime("%Y-%m-%d-%H-%M-%S")
    # file_name = f"{timestr+letters}.pdf"
    # pdf.output(file_name)
    # return file_name
    #return TABLE_DATA

##======================================for date between======================================================#############

# course = 'Data Communication'
# fromdate='2022-01-15'
# todate = '2022-02-10'
# teacher = 'Srabon'

def pdfONSearch(fromdate,todate,course,teacher):
    coms = (course, fromdate, todate)
    try:
        connection = sql.connect("FRASD1test.db")
        connection.row_factory = sql.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Attendance WHERE course = ? AND date BETWEEN ? AND ?", coms)
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append([x for x in row])  # or simply data.append(list(row))
        print(data)
        pdf = FPDF()
        pdf.add_page()
        page_width = pdf.w - 2 * pdf.l_margin
        pdf.set_font('Times', 'B', 14.0)
        title = f"Attendance report of {course}"
        date = f"from {fromdate} to {todate}"
        pdf.cell(page_width, 0.0, title, align='C')
        pdf.cell(page_width, 0.0, date, align="C")
        pdf.ln(10)
        pdf.set_font('Courier', '', 8)
        col_width = page_width / 4
        pdf.ln(1)
        th = pdf.font_size

        for row in data:
            pdf.cell(5, th * 1.5, str(row[0]), border=1, align="J")
            pdf.cell(15, th * 1.5, str(row[1]), border=1, align="J")
            pdf.cell(40, th * 1.5, row[3], border=1, align="J")
            pdf.cell(20, th * 1.5, row[4], border=1, align="J")

            pdf.ln(th * 1.5)

        pdf.ln(10)

        pdf.set_font('Times', '', 8)
        pdf.cell(page_width, 0.0, f"Generated by-:{teacher} ", align="R")
        pdf.cell(page_width, 0.0, '- end of report -', align='C')
        timestr = time.strftime("%Y-%m-%d-%H-%M-%S")
        pdffile = timestr+'.pdf'
        # pdf.output(f"{timestr + letters}.pdf")
        response = Response(pdf.output(dest='S'),mimetype='application/pdf')
        response.headers['Content-Disposition'] = f'attachment;filename={pdffile}'

        return response
    except Exception as e:
        print(e)
    finally:
        cursor.close()



