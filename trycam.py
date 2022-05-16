import time

import cv2
import os
def generate_dataset():
    face_classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)

        if faces is ():
            return None
        for (x, y, w, h) in faces:
            cropped_face = img[y:y + h, x:x + w]
        return cropped_face

    cap = cv2.VideoCapture(0)
    img_id = 0

    while True:
        ret, frame = cap.read()
        name="dummy"
        DATASET_PATH = os.path.join("datasets", name)
        if not os.path.isdir(DATASET_PATH):
            os.mkdir(DATASET_PATH)
        if face_cropped(frame) is not None:
            img_id += 1
            face = cv2.resize(face_cropped(frame), (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(os.path.join(DATASET_PATH, f"{name}_{img_id}.jpg"), frame)
            cv2.putText(face, str(img_id), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)
            time.sleep(0.5)

            cv2.imshow("Cropped_Face", face)
            if cv2.waitKey(1) == 13 or int(img_id) == 33:
                break

    cap.release()
    cv2.destroyAllWindows()
    print("Collecting samples is completed !!!")

generate_dataset()