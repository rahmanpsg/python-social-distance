import numpy as np
import cv2

NMS_THRESH = 0.25


def detect_people(frame, net, ln, MIN_CONF=0.45, isVideo=False, personIdx=0):
    # Ambil dimensi bingkai dan inisialisasi variabel results
    (H, W) = frame.shape[:2]
    results = []

    if isVideo:
        size = (540, 540)
        # size = (640, 640)
    else:
        size = (640, 640)
    # buat blob dari input frame
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, size,
                                 swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    # Inisialisai variabel untuk kotak yg terdeteksi, titik tengah, dan # confidences
    boxes = []
    centroids = []
    confidences = []

    # Lakukan perulangan dari masing2 layerOutputs
    for output in layerOutputs:
        # Lakukan perulangan untuk setiap data yang terdeteksi
        for detection in output:
            # Simpan nilai classID dan confidence
            # dari objek yang terdeteksi
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            # Filter pada objek yang terdeksi
            # Hanya mendeteksi orang dan nilai
            # confidence terpenuhi
            if classID == personIdx and confidence > MIN_CONF:

                # Simpan nilai kotak yang terdeksi
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # Tambahkan nilai kota, titik tengah, dan confidence
                boxes.append([x, y, int(width), int(height)])
                centroids.append((centerX, centerY))
                confidences.append(float(confidence))

    # Fungsi agar objek yang terdeteksi tidak terduplikasi
    # atau mendeteksi pada objek yang sama
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, MIN_CONF, NMS_THRESH)

    # Periksa apakah ada objek yang terdeksi
    if len(idxs) > 0:
        # Lakukan perulangan untuk nilai index yang tersimpan
        for i in idxs.flatten():
            # Simpan nilai koordinat kotak
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            # Perbaruhi nilai results yang akan dikembalikan
            r = (confidences[i], (x, y, x + w, y + h), centroids[i])
            results.append(r)

    # Kembalikan nilai results
    return results
