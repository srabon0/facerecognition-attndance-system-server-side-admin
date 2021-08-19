import flask
import werkzeug
import time
UPLOAD_FOLDER = "F:\\mypy\\PycharmProjects\\varsity\\uploaded"
import os
app = flask.Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def handle_request():
    files_ids = list(flask.request.files)
    print("\nNumber of Received Images : ", len(files_ids))
    image_num = 1
    for file_id in files_ids:
        print("\nSaving Image ", str(image_num), "/", len(files_ids))
        imagefile = flask.request.files[file_id]
        filename = werkzeug.utils.secure_filename(imagefile.filename)
        print("Image Filename : " + imagefile.filename)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        fname = (timestr+'_'+filename)
        file_loc = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], fname)
        filename.save(file_loc)
        image_num = image_num + 1
    print("\n")
    return "Image(s) Uploaded Successfully. Come Back Soon."

app.run(host="0.0.0.0", port=5000, debug=True)