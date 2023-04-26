import os
import json
import sys
import time
import tkinter as tk
import tkinter.messagebox as messagebox
import win32gui
import psutil

# Creates a password box for validated access
class PasswordWindow(tk.Tk):
    def __init__(self, on_password_entered):
        super().__init__()
        self.title('TimeWise')
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

# Creates a new frame for the time tracker
class TimeTrackerWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.time_data = []
        self.start_time = None
        self.active_windows = []
        self.time_spent = {}
    
    #Time tracking lables & buttons settings
    def create_widgets(self):
        self.timer_label = tk.Label(self, text='00:00:00', font=('Helvetica', 32))
        self.timer_label.pack(pady=20)

        self.start_button = tk.Button(self, text='Start', font=('Helvetica', 14), command=self.start_timer)
        self.start_button.pack(side='left', padx=10)

        self.stop_button = tk.Button(self, text='Stop', font=('Helvetica', 14), command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack(side='right', padx=10)

    #Starts the timer and starts polling for active windows
    def start_timer(self):
        self.start_time = time.time()
        self.active_windows = [self.get_active_window_title()]
        self.after(1000, self.update_time)
        self.after(100, self.poll_active_windows)
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    # Polls for active windows and updates active_windows list
    def poll_active_windows(self):
        active_window_title = self.get_active_window_title()
        if active_window_title != self.active_windows[-1]:
            self.active_windows.append(active_window_title)
        self.after(100, self.poll_active_windows)

    # Gets title of the current active window
    def get_active_window_title(self):
        active_window = None
        try:
            active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        except:
            pass
        return active_window
    

    def update_time(self):
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
            self.timer_label.config(text=time_str)

            # Get active window title
            active_window_title = self.get_active_window_title()

            # Add active window to active_windows list if not already present
            if active_window_title not in self.active_windows and active_window_title != 'TimeWise':
                self.active_windows.append(active_window_title)

            # Update time spent on current active window
            if active_window_title in self.time_spent:
                self.time_spent[active_window_title] += 1
            else:
                self.time_spent[active_window_title] = 1

        self.after(1000, self.update_time)

    def on_stop(self):
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
            self.time_data.append({'date': time.strftime('%Y-%m-%d %H:%M:%S'), 'windows': self.active_windows, 'time': time_str})

            # Write time data to file
            with open('time_data.json', 'a') as f:
                json.dump(self.time_data, f)

            self.start_time = None
            self.active_windows = []
            self.time_spent = {}
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def stop_timer(self):
        self.on_stop()        


# The main function for Timewise
def main():
    def on_password_entered():
        root = tk.Tk()
        root.title('Time Tracker')
        root.geometry('400x200')
        TimeTrackerWindow(master=root)
        root.mainloop()

    pw = PasswordWindow(on_password_entered=on_password_entered)
    pw.mainloop()


if __name__ == '__main__':
    main()
