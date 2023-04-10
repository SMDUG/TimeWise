import json
import sys
import time
import tkinter as tk
import win32gui
import psutil


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.time_data = []
        self.active_windows = []
        self.start_time = None
        self.create_widgets()

    def create_widgets(self):
        self.master.title('Time Tracker')
        self.master.protocol('WM_DELETE_WINDOW', self.on_exit)
        self.pack()

        self.time_label = tk.Label(self, text='00:00:00')
        self.time_label.pack()

        self.start_button = tk.Button(self, text='Start', command=self.on_start)
        self.start_button.pack()

        self.stop_button = tk.Button(self, text='Stop', command=self.on_stop)
        self.stop_button.pack()

    def on_start(self):
        self.start_time = time.time()
        self.active_windows = [self.get_active_window_title()]
        self.master.after(1000, self.update_time)
        self.master.after(100, self.poll_active_windows)

    def on_stop(self):
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
            self.time_data.append({'windows': self.active_windows, 'time': time_str})
            self.start_time = None
            self.active_windows = []

    def update_time(self):
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
            self.time_label.config(text=time_str)
        self.master.after(1000, self.update_time)

    def on_exit(self):
        """Save the time data to a JSON file and exit the application."""

        # Write the time data to a JSON file
        with open('time_data.json', 'w') as f:
            json.dump(self.time_data, f)

        # Destroy the GUI and exit the application
        self.master.destroy()
        sys.exit()

    def get_active_window_title(self):
        handle = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(handle)
        return title if title else 'Untitled'

    def poll_active_windows(self):
        if self.start_time is not None:
            active_window = self.get_active_window_title()
            if active_window not in self.active_windows:
                self.active_windows.append(active_window)
            self.master.after(100, self.poll_active_windows)


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
