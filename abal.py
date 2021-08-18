import cv2
from Recognition import recognize_cv2

test = cv2.imread('static/1.jpg')
faces = recognize_cv2(test)
print(faces)