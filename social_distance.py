from detection import detect_people
from tkinter import ttk
import math
import cv2
import numpy as np
from itertools import combinations
import time
from datetime import datetime
from PIL import ImageTk, Image
from playsound import playsound


def load_yolo(tiny=False):
    if tiny:
        cfg = "yolo/yolov4-tiny.cfg"
        weights = "yolo/yolov4-tiny.weights"
    else:
        cfg = "yolo/yolov4.cfg"
        weights = "yolo/yolov4.weights"

    # net = cv2.dnn.readNet("yolo/yolov4.weights", "yolo/yolov4.cfg")
    net = cv2.dnn.readNetFromDarknet(cfg, weights)
    # net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    # net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    layers_names = net.getLayerNames()
    output_layers = [layers_names[i[0]-1]
                     for i in net.getUnconnectedOutLayers()]
    return net, output_layers


def calculateDistance(p1, p2):
    # Menghitung Jarak Euclidean antara dua titik
    dst = math.sqrt(p1**2 + p2**2)
    return dst


def createBox(frame, model, output_layers,  min_treshold, min_confidence, isVideo=False, showJarakBerbahaya=False, alarm=False):
    results = detect_people(frame, model, output_layers,
                            min_confidence, isVideo)

    violate = set()
    colorDetect = (252, 132, 3)
    colorBerbahaya = (66, 66, 255)

    if len(results) >= 2:
        centroids = np.array([r[2] for r in results])

        for id1, id2 in combinations(centroids, 2):
            dx, dy = id1[0] - id2[0], id1[1] - id2[1]

            # Periksa jarak antar objek yang terdeksi
            distance = calculateDistance(dx, dy)
            toMeter = 100

            if distance / toMeter < (min_treshold / toMeter):
                violate.add(tuple(id1))
                violate.add(tuple(id2))

                if showJarakBerbahaya:
                    print("Xi = {}, Xj = {}, Yi = {}, Yj = {}, p1 = {}, p2 = {}".format(
                        id1[0], id2[0], id1[1], id2[1], dx**2, dy**2))
                    print("Jarak : {:.2f} meter".format(distance / toMeter))
                    draw_text(frame, "{:.2f} M".format(distance / toMeter), (255, 255, 255), pos=(
                        ((id1[0] + id2[0]) // 2) - 50, (id1[1] + id2[1]) // 2), font_scale=1, text_color_bg=(0, 0, 0))

                cv2.line(frame, (id1[0], id1[1]),
                         (id2[0], id2[1]), colorBerbahaya, 2)

        # Lakukan perulangan dari nilai results
    for (i, (confs, bbox, centroid)) in enumerate(results):
        # Simpan nilai kotak dan koordinat titik tengah
        # Inisialiasi warna kotak
        (startX, startY, endX, endY) = bbox
        (cX, cY) = centroid
        color = colorDetect

        # Periksa jika objek ada di list violate
        # Ubah warna kotak
        if tuple([cX, cY]) in violate:
            color = colorBerbahaya

        # menggambar kotak pembatas dari objek yang terdeksi
        # membuat circle pada titik tengah kotak
        cv2.rectangle(frame, (startX, startY), (endX, endY), color, 3)
        cv2.circle(frame, (cX, cY), 5, color, 1)

    totalTerdeteksi = len(results)
    totalBerbahaya = len(violate)

    if isVideo:
        pos = [(20, 20), (20, 60)]
        fontScale = 1
    else:
        pos = [(50, 50), (50, 120)]
        fontScale = 2
    draw_text(frame, "Total Terdeteksi : {}".format(
        totalTerdeteksi), colorDetect,  pos=pos[0], font_scale=fontScale)
    draw_text(frame, "Total Berbahaya : {}".format(totalBerbahaya),
              colorBerbahaya, pos=pos[1], font_scale=fontScale)

    if alarm and totalBerbahaya > 0:
        file = './alarm.wav'
        if isVideo:
            file = './beep.wav'
        playsound(file, block=False)

    # cv2.imshow("Frame", frame)


def draw_text(img, text,
              text_color,
              font_scale,
              font=cv2.FONT_HERSHEY_COMPLEX,
              pos=(0, 0),
              font_thickness=2,
              text_color_bg=(255, 255, 255)
              ):

    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    text_w += 10
    text_h += 10
    cv2.rectangle(img, pos, (x + text_w, y + text_h),
                  text_color_bg, cv2.FILLED)
    cv2.putText(img, text, (x + 5, y + text_h + font_scale - 10),
                font, font_scale, text_color, font_thickness, cv2.LINE_AA)

    return text_size


def detect_webcam(self, min_treshold=200, min_confidence=0.45, alarm=False):
    model, output_layers = load_yolo(tiny=True)
    # img = load_image(img_path)
    cap = cv2.VideoCapture(0)

    # print(width, height, fps)

    self.img = ttk.Label(self.outputFrame)
    self.img.pack()

    global play
    play = True

    def stop():
        global play
        play = False

    self.btnStop = ttk.Button(
        self.outputFrame, text="Berhenti", command=stop)
    self.btnStop.pack(pady=5)

    writer = None

    ts = time.time()

    output_path = "./histori/{}.avi".format(
        datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H-%M-%S'))

    while play:

        (grabbed, frame) = cap.read()
        if not grabbed:
            break

        # fps = cap.set(cv2.CAP_PROP_FPS, 25)
        # print(fps)

        createBox(frame, model, output_layers, min_treshold,
                  min_confidence, isVideo=True, alarm=alarm)

        # cv2.imshow("detections", img)

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(img)

        fixed_height = 450

        height_percent = (fixed_height / float(image.size[1]))
        width_size = int((float(image.size[0]) * float(height_percent)))

        image = image.resize((width_size, fixed_height), Image.NEAREST)

        photo = ImageTk.PhotoImage(image)

        self.img.config(image=photo)

        if writer is None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(output_path, fourcc, 25,
                                     (frame.shape[1], frame.shape[0]), True)
        if writer is not None:
            writer.write(frame)

        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    self.clearOutput()


def detect_image(img_path, min_treshold, min_confidence, showJarakBerbahaya, alarm):
    model, output_layers = load_yolo()
    img = cv2.imread(img_path)
    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    createBox(img, model, output_layers, min_treshold,
              min_confidence, showJarakBerbahaya=showJarakBerbahaya, alarm=alarm)

    # cv2.imshow("Deteksi", img)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img


def detect_video(path, min_treshold, min_confidence, showJarakBerbahaya, ttkProgress={}):
    model, output_layers = load_yolo(tiny=False)
    vc = cv2.VideoCapture(path)

    frame_count = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))

    print("total frame {}".format(frame_count))

    writer = None
    progress = 0
    max_progress = frame_count / 100

    ts = time.time()

    output_path = "./histori/{}.avi".format(
        datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H-%M-%S'))

    while True:
        key = cv2.waitKey(1)
        if key == 27:
            break
        (grabbed, frame) = vc.read()
        if not grabbed:
            break
        frame = cv2.resize(frame, (1200, 700))

        createBox(
            frame, model, output_layers, min_treshold, min_confidence, isVideo=True, showJarakBerbahaya=showJarakBerbahaya)

        progress += 1
        print(progress / max_progress)
        ttkProgress['value'] = progress / max_progress
        # cv2.imshow("detections", frame)

        if writer is None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(output_path, fourcc, 25,
                                     (frame.shape[1], frame.shape[0]), True)

        if writer is not None:
            writer.write(frame)

    t_sec = round(time.time() - ts)
    (t_min, t_sec) = divmod(t_sec, 60)
    (t_hour, t_min) = divmod(t_min, 60)
    print('Time passed: {}hour:{}min:{}sec'.format(t_hour, t_min, t_sec))

    return output_path


# detect_video('./assets/video6.mp4', {})
