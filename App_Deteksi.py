from operator import truediv
from turtle import delay
import cv2
from ultralytics import YOLO
import numpy as np
import time
import tkinter as tk
from tkinter import Label, PhotoImage, Tk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import requests 
# from twilio.rest import Client

model = YOLO('ModelYOLO/yolov8n_custom5.pt')
pesanSent = None

def output_video_default(frame):
    img_rgb_def = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil_def = Image.fromarray(img_rgb_def)
    imgtk = ImageTk.PhotoImage(image=img_pil_def)
    label_video_default.imgtk = imgtk
    label_video_default.configure(image=label_video_default.imgtk)

def output_video_deteksi(frame):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    imgtk = ImageTk.PhotoImage(image=img_pil)
    label_video_deteksi.imgtk = imgtk
    label_video_deteksi.configure(image=label_video_deteksi.imgtk)

def pilih_video():
    video_path = filedialog.askopenfilename(
        title="Pilih Video",
        filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
    )
    if video_path:
        proses_deteksi(video_path)
        

def gunakan_kamera_hp():
    input_ip = simpledialog.askstring("Input", "Masukkan IP & Port : \nContoh 192.168.1.12:8080")
    if input_ip :
        video_path = f'http://{input_ip}/video'
        proses_deteksi(video_path)


def kirim_notifikasi_telegram(pesan):
    token = '7312943209:AAHh7I0C2ZzgkaB6V5pSZ6Vkcqzc_eUXGmw'
    chat_id = '1117229740'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': pesan
    }
    requests.post(url, data=payload)

def proses_deteksi(video_path):
    global cap, count
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        messagebox.showerror("Error", "Deteksi Gagal. Silahkan Periksa Video atau Kamera anda.")
        return

    prev_time = 0
    

    # Area ROI
    roi_points = np.array([[4, 477], [2, 401], [299, 49], [460, 44], [618, 404], [617, 476], [4, 477]], np.int32)
    # roi_points = np.array([[4, 360], [288, 43], [439, 31], [607, 441], [1, 474]], np.int32)
    # roi_points = np.array([[49, 461], [253, 127], [349, 125], [476, 472], [49, 461]], np.int32)    
    # roi_points = np.array([[9, 476], [267, 79], [382, 86], [501, 475], [9, 476]], np.int32)    

    def update_frame():
        global pesanSent, count
        nonlocal prev_time
        berhasil, frame = cap.read()    

        current_time = time.time()
        frame_resized = cv2.resize(frame, (620, 440))
        frame_resized_def = cv2.resize(frame, (620, 440))

        # luas area ROI
        roi_area = cv2.contourArea(roi_points)
        
        # Gambar ROI
        cv2.polylines(frame_resized, [roi_points], isClosed=True, color=(0, 255, 255), thickness=2)

        # Inisialisasi penghitung kendaraan
        kendaraan_dalam_roi = {
            'Motor': {'jumlah': 0, 'area': 0},
            'Mobil': {'jumlah': 0, 'area': 0},
            'Truck': {'jumlah': 0, 'area': 0}
        }
        
        total_area_dalam_roi = 0
        
        # Deteksi objek
        results = model(frame_resized)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Hitung titik pusat
                pusat_x = (x1 + x2) // 2
                pusat_y = (y1 + y2) // 2
                
                confidence = box.conf[0]*100
                
                # Cek apakah pusat ada di ROI
                dalam_roi = cv2.pointPolygonTest(roi_points, (pusat_x, pusat_y), False) 
                
                if dalam_roi >= 0:
                    label = model.names[int(box.cls)]
                    area_box = (x2 - x1) * (y2 - y1)
                    
                    if label in kendaraan_dalam_roi:
                        kendaraan_dalam_roi[label]['jumlah'] += 1
                        kendaraan_dalam_roi[label]['area'] += area_box
                        total_area_dalam_roi += area_box
                        
                        # Gambar bounding box dan label
                        cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            frame_resized, f'{label} {confidence:.0f}%',  (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2
                        )            

        # Perhitungan persentase area
        kepadatan_area = (total_area_dalam_roi / roi_area) * 100

        if kepadatan_area >= 50:
            status_lalulintas = "Padat"
            warna_status = (0, 0, 255)
            if pesanSent != 1:
                kirim_notifikasi_telegram(f'Kepadatan area tinggi: {kepadatan_area:.0f}% area PADAT')
                pesanSent = 1
        elif kepadatan_area >= 30 and kepadatan_area < 50:
            status_lalulintas = "Sedang"
            warna_status = (0, 165, 255)
            pesanSent = 0
        else:
            status_lalulintas = "Lancar"
            warna_status = (0, 255, 0)
            pesanSent = 0
        

        cv2.putText(frame_resized, f'Motor: {kendaraan_dalam_roi["Motor"]["jumlah"]}', 
                    (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame_resized, f'Mobil: {kendaraan_dalam_roi["Mobil"]["jumlah"]}', 
                    (10, 49), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame_resized, f'Truck: {kendaraan_dalam_roi["Truck"]["jumlah"]}', 
                    (10, 76), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame_resized, f'Total Kendaraan: {sum(v["jumlah"] for v in kendaraan_dalam_roi.values())}', 
                    (10, 103), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        cv2.putText(frame_resized, f'FPS: {fps:.2f}', (10, 130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # status lalu lintas
        cv2.putText(frame_resized, f'Lalulintas: ', (10, frame_resized.shape[0] - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame_resized, f'{status_lalulintas}', (180, frame_resized.shape[0] - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, warna_status, 2)
        cv2.putText(frame_resized, f'Kepadatan Area: {kepadatan_area:.0f}%', 
                    (10, frame_resized.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        output_video_deteksi(frame_resized)
        output_video_default(frame_resized_def)

        label_video_deteksi.after(5, update_frame)

    update_frame()

def berhenti_deteksi():
    label_video_deteksi.configure(image='')
    label_video_default.configure(image='')
    cap.release()
    

# Tkinter
window = Tk()
window.title("Aplikasi Deteksi Kepadatan Lalulintas")
window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}")  
window.configure(bg = "#213555")

# # BG TOP
# keren = tk.Frame(window, width=1250, height=185, bd=2, relief="solid")
# keren.place(anchor="nw", x=15, y=10)

# JUDUL
text_title = tk.Label(window, text="Aplikasi Deteksi Kepadatan Lalulintas", font=('Helvetica', 25, 'bold'), bg="#213555", fg="White")
text_title.place(anchor="center", x=645, y=35 )

# BACKGROUND VIDEO DEFAULT
text_default = tk.Label(window, text="Output Video Default", font=('Helvetica', 12, 'bold'), bg="#213555", fg="white", height=2)
text_default.place(anchor="center", x=325, y=220 )

bg_video = tk.Frame(window, width=620, height=440, bd=2, relief="solid")
bg_video.place(anchor="center", x=325, y=455)
text_videoFrame = tk.Label(window, text="Tidak ada video yang diputar. Silakan pilih file video atau \naktifkan kamera untuk memulai deteksi.", font=('Helvetica', 13), fg="black", height=2)
text_videoFrame.place(anchor="center", x=325, y=455 )

# BACKGROUND VIDEO DETEKSI
text_default = tk.Label(window, text="Output Video Deteksi", font=('Helvetica', 12, 'bold'), bg="#213555", fg="white", height=2)
text_default.place(anchor="center", x=955, y=220 )

bg_video = tk.Frame(window, width=620, height=440, bd=2, relief="solid")
bg_video.place(anchor="center", x=955, y=455)
text_videoFrame = tk.Label(window, text="Tidak ada video yang diputar. Silakan pilih file video atau \naktifkan kamera untuk memulai deteksi.", font=('Helvetica', 13), fg="black", height=2)
text_videoFrame.place(anchor="center", x=955, y=455 )

# FRAME VIDEO DEFAULT
frame_video_default = tk.Frame(window, width=620, height=440)
frame_video_default.place(anchor="center", x=325, y=455)
label_video_default = tk.Label(frame_video_default,)
label_video_default.pack()

# FRAME VIDEO DETEKSI
frame_video_deteksi = tk.Frame(window, width=620, height=440)
frame_video_deteksi.place(anchor="center", x=955, y=455)
label_video_deteksi = tk.Label(frame_video_deteksi,)
label_video_deteksi.pack()

# BUTTON
btn_pilih_video = tk.Button(window, text="Pilih Video File", command=pilih_video, font=('Helvetica', 12, 'bold'), bg="#D9D9D9", fg="black", activebackground="#45a049", activeforeground="white", width=20, height=3)
btn_pilih_video.place(anchor="center", x=265, y=125 )

btn_kamera_hp = tk.Button(window, text="Gunakan Kamera", command=gunakan_kamera_hp, font=('Helvetica', 12, 'bold'), bg="#D9D9D9", fg="black", activebackground="#45a049", activeforeground="white", width=20, height=3)
btn_kamera_hp.place(anchor="center", x=515, y=125 )

btn_hentikan_deteksi = tk.Button(window, text="Hentikan Deteksi", command=berhenti_deteksi, font=('Helvetica', 12, 'bold'), bg="#D9D9D9", fg="black", activebackground="#45a049", activeforeground="white", width=20, height=3)
btn_hentikan_deteksi.place(anchor="center", x=765, y=125 )

btn_keluar = tk.Button(window, text="Keluar Aplikasi", command=window.quit, font=('Helvetica', 12, 'bold'), bg="#f44336", fg="white", activebackground="#000000", activeforeground="white", width=20, height=3)
btn_keluar.place(anchor="center", x=1015, y=125 )


window.mainloop()
