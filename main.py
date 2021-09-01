from tkinter.constants import END
from social_distance import detect_image, detect_video, detect_webcam
import tkinter as tk
from tkinter import Listbox, filedialog, ttk
from tkvideo import tkvideo
from ttkbootstrap import Style
from PIL import ImageTk, Image
import threading
from time import time
# import glob


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        style = Style(theme='cosmo')
        style.configure('.', font=('Poppins', 14))
        style.configure('TButton', font=('Poppins', 14))

        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.tabControl = ttk.Notebook(self)
        self.tabControl.configure(width=1024, height=720)

        self.tab1 = ttk.Frame(self.tabControl)
        self.tab2 = ttk.Frame(self.tabControl)

        self.tabControl.add(self.tab1, text="Deteksi Objek")
        # self.tabControl.add(self.tab2, text="Histori")
        self.tabControl.pack(expand=1, fill="both")

        self.img = None
        self.progress = None
        self.loading = None
        self.video = None
        self.btnStop = None

        self.widgets_tab1(self.tab1)
        # self.widgets_tab2(self.tab2)

    def widgets_tab1(self, tab):
        tab.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ttk.Label(tab,
                  text="Selamat Datang Di Aplikasi Pendeteksi Social Distancing", font='Poppins').grid(row=0, columnspan=6, pady=20)

        ttk.Label(tab,
                  text="Guswayani Gunawan", font='Poppins').grid(row=1, columnspan=6)

        ttk.Label(tab,
                  text="2019130004", font='Poppins').grid(row=2, columnspan=6)

        ttk.Button(
            tab, text="Buka Foto", width=20, command=self.open_image).grid(row=3, column=0, columnspan=2, sticky='e', pady=20)

        ttk.Button(
            tab, text="Buka Video", width=20, command=lambda: threading.Thread(target=self.open_video).start()).grid(row=3, column=2, columnspan=2)

        ttk.Button(
            tab, text="Buka Kamera", width=20, command=lambda: threading.Thread(target=self.open_webcam).start()).grid(row=3, column=4, columnspan=2, sticky='w')

        ttk.Label(tab,
                  text="Minimum Threshold", font='Poppins').grid(row=4, column=1)

        self.entryMinThreshold = ttk.Entry(tab)
        self.entryMinThreshold.insert(0, "200")
        self.entryMinThreshold.grid(row=4, column=2)

        ttk.Label(tab,
                  text="Minimum Confidence", font='Poppins').grid(row=4, column=3)

        self.entryMinConfidence = ttk.Entry(tab)
        self.entryMinConfidence.insert(0, "0.45")
        self.entryMinConfidence.grid(row=4, column=4)

        self.outputFrame = ttk.Labelframe(
            tab, text='Output', height=520)
        self.outputFrame.grid(row=5, columnspan=6,
                              sticky="news", padx=10, pady=10)

    def open_image(self):
        path = ""
        try:
            path = filedialog.askopenfilename()
        except Exception as e:
            path = filedialog.askopenfilename()
            pass

        if not path:
            return

        fixed_height = 480

        _start_time = time()

        # image = Image.open(path)
        img = detect_image(path, float(self.entryMinThreshold.get()),
                           float(self.entryMinConfidence.get()))
        image = Image.fromarray(img)

        height_percent = (fixed_height / float(image.size[1]))
        width_size = int((float(image.size[0]) * float(height_percent)))

        image = image.resize((width_size, fixed_height), Image.NEAREST)

        photo = ImageTk.PhotoImage(image)

        self.clearOutput()

        self.img = ttk.Label(self.outputFrame, image=photo)

        t_sec = round(time() - _start_time)
        (t_min, t_sec) = divmod(t_sec, 60)
        (t_hour, t_min) = divmod(t_min, 60)
        print('Time passed: {}hour:{}min:{}sec'.format(t_hour, t_min, t_sec))

        self.img.photo = photo
        self.img.pack()

    def open_video(self):
        path = ""
        try:
            path = filedialog.askopenfilename()
        except Exception as e:
            path = filedialog.askopenfilename()
            pass

        if not path:
            return

        self.clearOutput()

        self.progress = ttk.Progressbar(
            self.outputFrame, length=500)
        self.progress.pack()

        self.loading = ttk.Label(self.outputFrame,
                                 text="Memproses video...", font='Poppins')
        self.loading.pack()

        _start_time = time()

        output_path = detect_video(path, float(self.entryMinThreshold.get()),
                                   float(self.entryMinConfidence.get()), self.progress)

        t_sec = round(time() - _start_time)
        (t_min, t_sec) = divmod(t_sec, 60)
        (t_hour, t_min) = divmod(t_min, 60)
        print('Time passed: {}hour:{}min:{}sec'.format(t_hour, t_min, t_sec))

        self.clearOutput()

        self.video = ttk.Label(self.outputFrame)
        self.video.pack()

        self.player = tkvideo(output_path, self.video, size=(858, 480))

        try:
            self.player.play()
        except Exception as e:
            print(e)
            pass

    def open_webcam(self):
        self.clearOutput()

        detect_webcam(self, float(self.entryMinThreshold.get()),
                      float(self.entryMinConfidence.get()))

    def clearOutput(self):
        if(self.img != None):
            self.img.config(image='')
            self.img.pack_forget()

        if(self.progress != None):
            self.loading.pack_forget()
            self.progress.pack_forget()

        if(self.video != None):
            self.video.pack_forget()

        if(self.btnStop != None):
            self.btnStop.pack_forget()

    #
    # def widgets_tab2(self, tab):
    #     self.outputFrame2 = ttk.Labelframe(
    #         tab, text='Daftar Histori', height=520)
    #     self.outputFrame2.pack(fill='both', padx=10, pady=10)

    #     daftarHistori = glob.glob("./histori/*.avi")

    #     listBox = Listbox(self.outputFrame2)
    #     listBox.pack()

    #     for histori in daftarHistori:
    #         listBox.insert(END, histori)
    #         # ttk.Label(self.outputFrame2,
    #         #           text=histori, font='Poppins').pack()


root = tk.Tk(className='- Aplikasi Deteksi Objek -')
app = Application(master=root)
app.mainloop()
