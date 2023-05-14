"""
Author:  Christian Ahialegbedzi
Date written: 03/30/23
Short Desc:   TimeWise provides an fast and simple solution for tracking your time.
"""
import os
import json
import sys
import time
import tkinter as tk
import tkinter.messagebox as messagebox
import datetime
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
        
        #Button settings
        self.password_label = tk.Label(self, text='Enter password:', font=('Helvetica', 14))
        self.password_label.pack(pady=10)

        self.password_entry = tk.Entry(self, show='*', font=('Helvetica', 14))
        self.password_entry.pack(pady=10)
        self.password_entry.config(validate="key", validatecommand=(self.register(self.validate_password_entry), '%P'))

        self.submit_button = tk.Button(self, text='Submit', font=('Helvetica', 14), command=self.check_password)
        self.submit_button.pack(pady=10)
    
    #checks if entered password is correct
    def check_password(self):
        if self.password_entry.get() == 'password':
            self.password_correct = True
            self.destroy()
            if self.on_password_entered is not None:
                self.on_password_entered()
        else:
            messagebox.showerror('Error', 'Incorrect password. Please try again.')

    def validate_password_entry(self, password):
        if all(c.isalnum() or c == '_' for c in password):
            return True
        else:
            messagebox.showerror('Error', 'Invalid password. Password can only contain alphabetic characters, digits, and underscores.')
            return False
        

# Creates a new frame for the time tracker
class TimeTrackerWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.time_data = {'activities': []}
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

        self.exit_button = tk.Button(self, text='Exit', font=('Helvetica', 14), command=self.on_exit,)
        self.exit_button.pack(side='right', padx=10)

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
        #if active_window_title != self.active_windows[-1]:
        if self.active_windows and active_window_title != self.active_windows[-1]:

            self.active_windows.append(active_window_title)
        self.after(1000, self.poll_active_windows)

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
    print('on_stop called')
    def on_stop(self):
        try:
            if self.start_time is not None:
                elapsed_time = time.time() - self.start_time
                time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))

                # Starts self.time_data as a dictionary with an empty list for the 'activities' key
                if not isinstance(self.time_data, dict):
                    self.time_data = {'activities': []}

                # Check if the 'activities' key exists in self.time_data
                if 'activities' not in self.time_data:
                    self.time_data['activities'] = []
                   

                # Create new dictionary for the current time entry
                time_entry = {
                    'start_time': datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'days': 0,
                    'hours': int(elapsed_time // 3600),
                    'minutes': int((elapsed_time // 60) % 60),
                    'seconds': int(elapsed_time % 60)
                }

                # Add the current time entry to the appropriate window in the time_data list
                if self.active_windows:
                    last_window = self.active_windows[-1]
                    for activity in self.time_data['activities']:
                        if activity['name'] == last_window:
                            activity['time_entries'].append(time_entry)
                            break
                    else:
                        self.time_data['activities'].append({'name': last_window, 'time_entries': [time_entry]})
                else:
                    # If no window was active, add the time entry to the "untracked" activity
                    for activity in self.time_data['activities']:
                        if activity['name'] == '':
                            activity['time_entries'].append(time_entry)
                            break
            
                # Write time data to file
                with open('time_data.json', 'w') as f:
                    json.dump(self.time_data, f, indent=4)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            return    

    def stop_timer(self):
        self.on_stop()
        if self.start_time is None:
            return
        elapsed_time = time.time() - self.start_time
        self.time_spent[self.active_windows[-1]] += elapsed_time
        self.active_windows.pop()
        self.start_time = None
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED) 

    def on_exit(self):
        self.stop_timer
        self.master.destroy()       


# The main function for Timewise
def main():
    def on_password_entered():
        root = tk.Tk()
        root.title('TimeWise')
        root.geometry('400x200')
        TimeTrackerWindow(master=root)
        root.mainloop()

    pw = PasswordWindow(on_password_entered=on_password_entered)
    pw.mainloop()


if __name__ == '__main__':
    main()
