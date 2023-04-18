import os
import json
import sys
import time
import tkinter as tk
import tkinter.messagebox as messagebox
import win32gui
import psutil


class PasswordWindow(tk.Tk):
    def __init__(self, on_password_entered):
        super().__init__()
        self.title('Password')
        self.geometry('400x200')
        self.resizable(False, False)
        self.password_correct = False
        self.on_password_entered = on_password_entered

        self.password_label = tk.Label(self, text='Enter password:', font=('Helvetica', 14))
        self.password_label.pack(pady=10)

        self.password_entry = tk.Entry(self, show='*', font=('Helvetica', 14))
        self.password_entry.pack(pady=10)

        self.submit_button = tk.Button(self, text='Submit', font=('Helvetica', 14), command=self.check_password)
        self.submit_button.pack(pady=10)

    def check_password(self):
        if self.password_entry.get() == 'password':
            self.password_correct = True
            self.destroy()
            if self.on_password_entered is not None:
                self.on_password_entered()
        else:
            messagebox.showerror('Error', 'Incorrect password. Please try again.')


class Application(tk.Tk):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.time_data = []
        self.active_windows = []
        self.start_time = None
        self.create_widgets()
        self.pack()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def create_widgets(self):
        self.title('Time Tracker')
        self.geometry('600x400')
        self.resizable(False, False)
        self.withdraw()

        #frame = tk.Frame(self)
        #frame.pack(fill=tk.BOTH, expand=True)

        self.time_label = tk.Label(self, text='00:00:00', font=('Helvetica', 18))
        self.time_label.pack(pady=10)

        self.start_button = tk.Button(self, text='Start', font=('Helvetica', 14), command=self.on_start)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(self, text='Stop', font=('Helvetica', 14), command=self.on_stop, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.quit_button = tk.Button(self, text='Quit', font=('Helvetica', 14), command=self.on_exit)
        self.quit_button.pack(pady=10)

    def on_start(self):
        self.start_time = time.time()
        self.active_windows = [self.get_active_window_title()]
        self.after(1000, self.update_time)
        self.after(100, self.poll_active_windows)
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def on_stop(self):
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
            self.time_data.append({'windows': self.active_windows, 'time': time_str})
            self.start_time = None
            self.active_windows = []
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def update_time(self):
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
            self.time_label.config(text=time_str)
        self.after(1000, self.update_time)

    def on_exit(self):
        #Save the time data to a JSON file and exit the application.

        # Write the time data to a JSON file
        with open('time_data.json', 'w') as f:
            json.dump(self.time_data, f, indent=4)

        # Destroy the GUI and exit the
        self.destroy()
        sys.exit()

    def get_active_window_title(self):
        if sys.platform == 'win32':
            window = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(window)
            if title:
                return title
            elif sys.platform == 'darwin':
                script = 'tell application "System Events" to get name of first application process whose frontmost is true'
                title = subprocess.check_output(['/usr/bin/osascript', '-e', script])
                title = title.decode('utf-8').strip()
                if title:
                    return title
                else:
                    return 'Unknown window'
        else:
            return 'Unknown platform'

if __name__ == '__main__':
    # Define a function that will create the Application instance
    def create_app():
        root = tk.Tk()
        app = Application(master=root)
        app.title('Time Tracker')  # Set the title of the window
        app.mainloop()  # Start the GUI event loop
    
    # Create password window to prompt for password
    pw = PasswordWindow(on_password_entered=create_app)

    # Start the Tkinter event loop
    pw.mainloop()
