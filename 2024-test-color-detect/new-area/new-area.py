import cv2

# Inisialisasi kamera
cap = cv2.VideoCapture(0)



while True:
    # Baca frame dari kamera
    ret, frame = cap.read()
    if not ret:
        break

    box_size = 100;
    
    # Ukuran frame
    frame_height, frame_width, _ = frame.shape

    # Koordinat kotak
    start_x = frame_width - box_size
    start_y = frame_height - box_size
    end_x = frame_width
    end_y = frame_height

    # Koordinat sudut kiri bawah
    start_x_left_bottom = start_x
    start_y_left_bottom = frame_height

    # Koordinat sudut kanan atas
    start_x_right_top = frame_width
    start_y_right_top = start_y

    # Menggambar kotak
    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 0, 0), 2)

    cv2.line(frame, (int(frame_width/2), 0), (int(frame_width/2), frame_height),  (255, 255, 255), 2)
    cv2.line(frame, (0, int(frame_height/2)), (frame_width, int(frame_height/2)), (255,255,255), 2)

    # Menggambar garis diagonal dari sudut kiri bawah
    cv2.line(frame, (int(frame_width/2-(box_size+50)), 0), (start_x_left_bottom, start_y_left_bottom), (0, 0, 255), 2)

    # Menggambar garis diagonal dari sudut kanan atas
    cv2.line(frame,  (int(frame_width/2+(box_size+50)), 0), (start_x_right_top, start_y_right_top), (0, 0, 255), 2)

    # # Menggambar kamera
    # camera_width = 50
    # camera_height = 30
    # camera_x = 200
    # camera_y = 100
    # cv2.rectangle(frame, (camera_x, camera_y), (camera_x + camera_width, camera_y + camera_height), (0, 255, 0), 2)

    # Menampilkan frame yang telah dimodifikasi
    cv2.imshow('Frame', frame)

    # Tunggu tombol 'q' ditekan untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Menutup kamera dan menghentikan semua jendela
cap.release()
cv2.destroyAllWindows()
