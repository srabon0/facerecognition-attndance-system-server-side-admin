from flask import jsonify
import cv2
from Recognition import recognize_cv2

test = cv2.imread('test1.jpg')
faces = recognize_cv2(test)
aq_face = []
print(faces)
for face in faces:
    if (face['top_prediction']['confidence']) > 0.90:
        aq_face.append(face['top_prediction']['label'])
print(aq_face)

inse = jsonify(faces)
print(inse)
results =['8171013', '8171063', '8171045', '8171049', '8171013', '8171013', '8171013', '8171049', '8171013']
results = list(map(int, results))
print(type(results[0]))