from flask import Flask, render_template, Response, request
import cv2
import datetime, time
import os, sys
import numpy as np
from threading import Thread
from facenet_pytorch import MTCNN
from PIL import Image
global capture, rec_frame, grey, switch, neg, face, rec, out
capture = 0
grey = 0
neg = 0
face = 0
switch = 1
rec = 0

# make shots directory to save pics
try:
    os.mkdir('./shots')
except OSError as error:
    pass

name = str(input("Person Name: "))
DATASET_PATH = os.path.join("datasets", name)
if not os.path.isdir(DATASET_PATH):
  os.mkdir(DATASET_PATH)

# Load pretrained face detection model

# instatiate flask app
app = Flask(__name__, template_folder='./templates')
mtcnn = MTCNN(prewhiten=False, keep_all=True, thresholds=[0.6, 0.7, 0.9])

camera = cv2.VideoCapture(0)




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
                        capture = 0

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


@app.route('/')
def index():
    return render_template('index2.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/requests', methods=['POST', 'GET'])
def tasks():
    global switch, camera
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
    app.run()

camera.release()
cv2.destroyAllWindows()