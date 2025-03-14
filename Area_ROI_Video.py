import cv2
import numpy as np

# Fungsi callback untuk mendapatkan koordinat pixel saat diklik
def show_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Jika tombol kiri mouse diklik
        print(f"Koordinat yang diklik: ({x}, {y})")

# Buka video
video_path = 'Video/SEPEDA.mp4'  # Ganti dengan path video Anda
cap = cv2.VideoCapture(video_path)

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
    if key == ord('q'):  # Tekan 'q' untuk keluar
        break
    elif key == ord('p'):  # Tekan 'p' untuk pause/play
        paused = not paused
    
cap.release()
cv2.destroyAllWindows()

