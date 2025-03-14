import cv2
import numpy as np


def show_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  
        print(f"Koordinat yang diklik: ({x}, {y})")

# Buka kamera
ip_address = "http://192.168.91.174:8080/video"  
cap = cv2.VideoCapture(ip_address)  

paused = False
cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Video', 640, 480)
cv2.setMouseCallback('Video', show_coordinates)

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.resize(frame, (620, 480))
        
    cv2.imshow('Video', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): 
        break
    elif key == ord('p'): 
        paused = not paused
    
cap.release()
cv2.destroyAllWindows()

