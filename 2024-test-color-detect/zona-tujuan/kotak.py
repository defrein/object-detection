import cv2
import numpy as np

def on_trackbar_move_horizontal(pos):
    global start_x
    start_x = pos

def on_trackbar_move_vertical(pos):
    global start_y
    start_y = pos

def on_trackbar_resize(size):
    global box_size
    box_size = size

def reset_position(width, height):
    global start_x, start_y
    start_x = int((width - box_size) / 2)
    start_y = int((height - box_size) / 2)
    cv2.setTrackbarPos('Start X', 'Trackbars', start_x)
    cv2.setTrackbarPos('Start Y', 'Trackbars', start_y)

def main():
    # Membuka kamera
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    
    # Memeriksa apakah kamera berhasil dibuka
    if not cap.isOpened():
        print("Error: Gagal membuka kamera.")
        return
    
    ret, frame = cap.read()
    
    # Inisialisasi variabel untuk posisi awal kotak dan ukuran kotak
    global start_x, start_y, box_size
    height, width, _ = frame.shape
    box_size = 100
    start_x = int((width - box_size) / 2)
    start_y = int((height - box_size) / 2)

    # Membuat jendela untuk trackbars
    cv2.namedWindow('Trackbars', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Trackbars', 300, 200)

    cv2.createTrackbar('Start X', 'Trackbars', start_x, width - box_size, on_trackbar_move_horizontal)

    # Membuat trackbar untuk menggeser kotak secara vertikal
    cv2.createTrackbar('Start Y', 'Trackbars', start_y, height - box_size, on_trackbar_move_vertical)

    # Membuat trackbar untuk mengatur ukuran kotak
    cv2.createTrackbar('Box Size', 'Trackbars', box_size, min(height, width), on_trackbar_resize)

    
    while True:
        # Membaca frame dari kamera
        ret, frame = cap.read()
        
        # Memeriksa apakah frame berhasil dibaca
        if not ret:
            print("Error: Gagal membaca frame.")
            break
        
        
        # Mengambil ukuran frame
        height, width, _ = frame.shape
        
        # Menggambar kotak pada frame
        end_x = start_x + box_size
        end_y = start_y + box_size

        
        # Memastikan kotak tidak melebihi batas frame
        start_x = max(0, min(start_x, width - box_size))
        start_y = max(0, min(start_y, height - box_size))
        end_x = min(width, start_x + box_size)
        end_y = min(height, start_y + box_size)
        
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
        
        # Menggambar garis yang mengikat sudut kotak ke ujung sudut frame
        cv2.line(frame, (start_x, start_y), (0, 0), (255, 0, 0), 2)  # Sudut kiri atas
        cv2.line(frame, (end_x, start_y), (width, 0), (255, 0, 0), 2)  # Sudut kanan atas
        cv2.line(frame, (start_x, end_y), (0, height), (255, 0, 0), 2)  # Sudut kiri bawah
        cv2.line(frame, (end_x, end_y), (width, height), (255, 0, 0), 2)  # Sudut kanan bawah
        
        # Menggambar area dengan nama dan label transparan
        mask = np.zeros_like(frame, dtype=np.uint8)
        
        # Atas
        cv2.putText(mask, "Atas", (int(width/2), int(start_y/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Bawah
        cv2.putText(mask, "Bawah", (int(width/2), int((height+end_y)/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Kiri
        cv2.putText(mask, "Kiri", (int(start_x/2)-25, int((height+start_y)/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Kanan
        cv2.putText(mask, "Kanan", (int((width+end_x)/2)+10, int((height+start_y)/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Menambahkan mask ke frame
        frame = cv2.addWeighted(frame, 1, mask, 0.5, 0)
        
        # Menampilkan frame
        cv2.imshow('Camera', frame)
        
        # Mendeteksi input keyboard
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('r'):  # Reset posisi kotak ketika tombol 'r' ditekan
            reset_position(width, height)
        
        # Memperbarui area koordinat kotak setelah pergeseran
        box_area = (start_x, start_y, end_x, end_y, height, width)
        print("Area koordinat kotak:", box_area)
    
    # Melepaskan kamera dan menutup jendela
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
