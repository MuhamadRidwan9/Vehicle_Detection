import cv2
import numpy as np

# Fungsi callback untuk mendapatkan koordinat pixel saat diklik
def show_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Jika tombol kiri mouse diklik
        print(f"Koordinat yang diklik: (x={x}, y={y})")

# Memuat gambar jpg menggunakan OpenCV
image_path = 'DataCostumVehicle/Vehicle333.jpg'  # Ganti dengan path gambar jpg Anda
img = cv2.imread(image_path)

image = cv2.resize(img, (640, 480))

# Menampilkan gambar di jendela
cv2.imshow('Gambar', image)

# Mengatur callback mouse untuk jendela gambar
cv2.setMouseCallback('Gambar', show_coordinates)

# Tunggu hingga tombol 'q' ditekan untuk keluar
while True:
    cv2.imshow('Gambar', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

