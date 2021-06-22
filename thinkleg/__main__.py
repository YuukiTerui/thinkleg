import os
from tasks.frames.baseframe import BaseFrame
from tasks.apps.baseapp import BaseApp
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from json import load
from logging import config, getLogger
with open('./config/log_conf.json', 'r') as f:
    config.dictConfig(load(f))

from tasks.apps.baseapp import BaseApp
from tasks.frames.tasks import TasksFrame
from tasks.frames.vas import VasFrame
from tasks.frames.mentalcalc import MentalCalcFrame
from arduino import Arduino
from mysocket.server import ThinkLegServer


class ThinkLegApp(BaseApp):
    def __init__(self, datapath):
        
        self.logger = getLogger('thinkleg')
        self.datapath = datapath
        self.server = ThinkLegServer(host='localhost', port=12345)
        self.server.start()

        self.arduino = Arduino(path=self.datapath, fname='arduino')
        self.arduino.start()

        super().__init__()
        self.title('ThinkLegTaskApp')
        self.first = FirstFrame(self)
        self.first.grid(row=0, column=0)
        self.appframe = None
        #self.set_frame('first')

        self.logger.debug('ThinkLegApp is initialized.')

    def __setattr__(self, name, value) -> None:
        if name == 'frame' and value == None:
            self.arduino.thinkleg_status = 'first'
        return super().__setattr__(name, value)

    def set_frame(self, to):
        self.logger.debug('set_frame is called.')
        if to == 'vas':
            self.arduino.thinkleg_status = 'vas'
            self.frame = VasFrame(self, self.datapath, 'vas')
        elif 'mentalcalc' in to:
            self.arduino.thinkleg_status = 'mentalcalc'
            self.frame = MentalCalcFrame(int(to[-1]), self, self.datapath)
        self.frame.grid(row=0, column=0, sticky='nsew')
    
    def finish(self):
        self.arduino.save('thinkleg')
        return super().finish()



class FirstFrame(BaseFrame):
    def __init__(self, master):
        super().__init__(master=master)
        self.create_widgets()
        

    def create_widgets(self):
        self.grid(row=0, column=0, sticky='nsew')
        title_font = ('System', 100, 'bold', 'italic', 'underline', 'overstrike')
        self.title_label = tk.Label(self, text='Think Leg System', font=title_font)
        self.title_label.pack(pady=10, expand=True, fill=tk.X)

        self.task_frame = self.create_taskframe()
        self.task_frame.pack(pady=10)

        self.progress_frame = tk.Frame(self)
        self.progress_label = tk.Label(self.progress_frame, text='Preparing for Arduino')
        self.progress_label.pack()
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(self.progress_frame,
            orient=tk.HORIZONTAL, variable=self.progress_var, maximum=60, length=200, mode='determinate'
        )
        self.progress_bar.pack()
        self.progress_frame.pack()
        if self.master.arduino:
            threading.Thread(target=self.__progress, daemon=True).start()
        
        self.finish_button = tk.Button(self, text='finish', width=20, height=5, command=lambda: self.master.finish())
        self.finish_button.pack(padx=50, pady=50, side=tk.BOTTOM, anchor=tk.SE)
    
    def create_taskframe(self):
        frame = tk.LabelFrame(self, text='Tasks', font=('System', 60))
        padx = 50
        self.vas_frame = tk.LabelFrame(frame, text='VAS', font=('System', 30))
        self.tapping_frame = tk.LabelFrame(frame, text='Tapping', font=('System', 30))
        self.mentalcalc_frame = tk.LabelFrame(frame, text='MentalCalc', font=('System', 30))

        self.vas_frame.pack(padx=padx, side=tk.LEFT)
        self.tapping_frame.pack(padx=padx, side=tk.LEFT)
        self.mentalcalc_frame.pack(padx=padx, side=tk.LEFT)

        btn_w, btn_h = 10, 2
        self.vas_button = tk.Button(self.vas_frame, text='start', width=btn_w, height=btn_h, command=lambda:self.set_frame('vas'))
        self.vas_button.pack()

        self.radio_var_mentalcalc = tk.IntVar(value=2)
        self.mentalcalc_radio1 = tk.Radiobutton(self.mentalcalc_frame, value=2, variable=self.radio_var_mentalcalc, text='Low')
        self.mentalcalc_radio2 = tk.Radiobutton(self.mentalcalc_frame, value=4, variable=self.radio_var_mentalcalc, text='High')
        self.mentalcalc_radio1.pack()
        self.mentalcalc_radio2.pack()
        self.mentalcalc_button = tk.Button(self.mentalcalc_frame, text='start', width=btn_w, height=btn_h,
            command=lambda:self.set_frame(f'mentalcalc{self.radio_var_mentalcalc.get()}')
        )
        self.mentalcalc_button.pack()
        return frame

    def __progress(self):
        st = time.time()
        latency = 60
        t = 0
        while t < latency:
            t = time.time()-st
            self.progress_var.set(t)
            time.sleep(1)
        self.progress_label['text'] = 'Arduino Ready.'
        self.progress_bar.destroy()

    def set_frame(self, to):
        self.master.set_frame(to)


def main():
    datapath = f'./data/{datetime.now().strftime("%Y%m%d/%H-%M-%S")}/'
    os.makedirs(datapath, exist_ok=True)

    app = ThinkLegApp(datapath)
    app.mainloop()



if __name__ == '__main__':
    main()