from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageTk
from bs4 import BeautifulSoup
import customtkinter as ctk
import urllib.request
import subprocess
import threading
import requests
import time
import sys
import os

def main():
    app = WindowController()
    app.root.mainloop()

def isLinux():
    return sys.platform.startswith('linux')

def isWindows():
    return sys.platform.startswith('nt')

def err_msg(master, msg):
    error = CTkMessagebox(master=master, icon='cancel', message=msg, option_focus=1, button_color="#950808", button_hover_color="#630202")
    error.get()

def dynamic_resolution(d_root, d_width, d_height):
    screen_height = d_root.winfo_screenheight()
    screen_width = d_root.winfo_screenwidth()
    x = (screen_width // 2) - (d_width // 2)
    y = (screen_height // 2) - (d_height // 2)
    d_root.geometry(f"{d_width}x{d_height}+{x}+{y}")

def grab_icon(icon:str):
    try:
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(os.path.dirname(sys.executable), icon)
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.getcwd(), icon)
        else:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), icon)
        return icon_path
    except Exception:
        pass

def set_window_icon(root):
    try:
        if isWindows():
            icon_path = grab_icon('icon.ico')

            if os.path.exists(icon_path):
                root.after(150, root.iconbitmap(icon_path))
        else:
            icon_path = grab_icon('icon.png')
            
            if os.path.exists(icon_path):
                pil_img = Image.open(icon_path).convert("RGBA")
                imagetk = ImageTk.PhotoImage(pil_img)
                root.iconphoto(False, imagetk)
    except Exception:
        pass

class WindowController:  # receives and manages views' calls and models
    CURRENT_VERSION = "v1.1.0"
    def __init__(self):
        self.different_version = False
        self.previous_window = None
        self.current_window = None
        self.is_stopwatch_running = False
        self.is_timer_running = False
        self.timer_first_run = True
        
        self.root = ctk.CTk()
        self.root.withdraw()
        
        self.stopwatch_model = StopwatchModel()
        self.timer_model = TimerModel()
        
        self.show_stopwatch()
        self.previous_window = self.current_window
        
        self.auto_update_thread()
    
    def fetch_git_version(self):
        try:
            url = "https://github.com/Guilherme-A-Garcia/Kronos/releases/latest"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            git_version = soup.find('span', class_='css-truncate-target').text.strip()
            print(f"GitHub located version: {git_version}")
            
            if git_version != WindowController.CURRENT_VERSION:
                self.different_version = True
        except Exception as e:
            print(f"Error locating the GitHub version: {e}")
    
    def auto_update_thread(self):
        def update_thread(inputted_thread):
            if inputted_thread.is_alive():
                self.current_window.after(10, lambda: update_thread(inputted_thread))
            else:
                print(f"Thread ({inputted_thread}) finished successfully!")
                if inputted_thread == self.thread1:
                    check_update()
                    
        self.thread1 = threading.Thread(target=self.fetch_git_version)
        self.thread1.start()
        update_thread(self.thread1)
        
        def check_update():
            if self.different_version:
                msg = CTkMessagebox(message="A newer version has been detected, would you like to update the app?", option_1='Yes', option_2='No', option_focus=2, button_color="#950808", button_hover_color="#630202")
                if msg.get() == 'Yes':
                    self.show_updating_window()
                    self.thread2 = threading.Thread(target=self.update_app)
                    self.thread2.start()
                    update_thread(self.thread2)
            else:
                return
    
    def update_app(self):
        url = ''
        file_path = ''
        cwd = self.get_app_dir()
        
        print(f"Resolved update directory: {cwd}")
        
        if os.path.exists(cwd):
            if isLinux():
                url = 'https://github.com/Guilherme-A-Garcia/Kronos/releases/latest/download/Kronos-x86_64.AppImage'
                file_path = os.path.join(cwd, 'Kronos-x86_64-NEW.AppImage')
            else:
                url = 'https://github.com/Guilherme-A-Garcia/Kronos/releases/latest/download/Kronos.exe'
                file_path = os.path.join(cwd, 'Kronos-NEW.exe')
            
            print(f'Downloading to: {file_path}')

            try:
                urllib.request.urlretrieve(url, file_path)
            except Exception as e:
                err_msg(master=self.current_window, msg=f"An error occurred while downloading the update, the application will now close: {e}")
                self.root.destroy()

            success_msg = CTkMessagebox(master=self.current_window, title='Success', message="Update finished successfully. Closing application...", icon="check", option_focus=1, button_color="#950808", button_hover_color="#630202")
            success_msg.get()
            self.close_and_rename()

    def get_app_dir(self):
        if getattr(sys, 'frozen', False):
            try:
                path = os.path.abspath(sys.argv[0])
                dir_path = os.path.abspath(path)
                if os.path.exists(dir_path):
                    return dir_path
            except Exception:
                pass
            
            try:
                cwd = os.getcwd()
                if os.path.exists(cwd):
                    return cwd
            except Exception:
                pass
            
            try:
                temp_dir = os.path.dirname(sys.executable)
                parent = os.path.abspath(os.path.join(temp_dir, '..'))
                if os.path.exists(parent):
                    return parent
            except Exception:
                pass
        return os.getcwd()
    
    def start_timer(self):
        if self.is_timer_running:
            return
        
        if all(not entry.get().strip() for entry in self.current_window.entries) or all(entry.get().strip() in ('h', 'm', 's') for entry in self.current_window.entries):
            err_msg(master=self.current_window, msg='Error: Please enter a number in at least one field.')
            self.reset_timer()
            return
        
        for entry in self.current_window.entries:
            if entry.get().strip() not in ('h', 'm', 's') and not entry.get().strip().isdigit():
                err_msg(master=self.current_window, msg='Error: Enter valid numbers.')
                self.reset_timer()
                return
            
        self.is_timer_running = True
        self.current_window.timer_stop.configure(state='normal')
        self.current_window.timer_start.configure(state='disabled')
        self.current_window.timer_reset.configure(state='normal')
        
        for entry in self.current_window.entries:
            self.current_window.after(0, lambda entry=entry: entry.grid_forget())
        
        self.current_window.after(0, self.current_window.minutes_seconds_separation.grid_forget)
        self.current_window.after(0, self.current_window.hours_minutes_separation.grid_forget)
            
        self.current_window.timer_counter_label.grid(padx=2, pady=2, row=0, column=2)
        
        hours = int(self.current_window.entries[0].get() if self.current_window.entries[0].get() != 'h' else '0')
            
        minutes = int(self.current_window.entries[1].get() if self.current_window.entries[1].get() != 'm' else '0')
        
        seconds = int(self.current_window.entries[2].get() if self.current_window.entries[2].get() != 's' else '0')
        
        if (hours, minutes, seconds) == (0, 0, 0):
            err_msg(master=self.current_window, msg='Error: Enter numbers bigger than zero.')
            self.reset_timer()
            return
        
        self.last_timer_iteration = time.perf_counter()
        
        if self.timer_first_run:
            self.timer_model.receive_timer_counter(hour=hours, minutes=minutes, sec=seconds)
                
        def loop():
            remaining = self.timer_model.get_remaining_time()
            if self.is_timer_running and remaining > 0:
                current_timer_iteration = time.perf_counter()
                timer_delta_time = current_timer_iteration - self.last_timer_iteration
                self.last_timer_iteration = current_timer_iteration
                
                self.timer_model.timer_process_time()
                self.current_window.after(0, lambda: self.current_window.timer_counter_label_strvar.set(value=self.timer_model.timer_process_time()))
                self.timer_model.detract_remaining_time(timer_delta_time)

                self.current_window.after(10, loop)
        
        self.timer_first_run = False
        loop()
    
    def stop_timer(self):
        if self.is_timer_running:
            self.is_timer_running = False
        
        self.current_window.timer_stop.configure(state='disabled')
        self.current_window.timer_start.configure(state='normal')
    
    def reset_timer(self):
        self.timer_first_run = True
        stringvars = [(self.current_window.timer_hours_stringvar, 'h'), (self.current_window.timer_minutes_stringvar, 'm'), (self.current_window.timer_seconds_stringvar, 's')]
        self.stop_timer()
        self.current_window.timer_reset.configure(state='disabled')

        self.current_window.entries[0].grid(padx=(20, 10), pady=2, column=0, row=0, sticky='nsew')
        self.current_window.entries[1].grid(padx=15, pady=2, column=2, row=0, sticky='nsew')
        self.current_window.entries[2].grid(padx=(10, 20), pady=2, column=4, row=0, sticky='nsew')

        self.current_window.minutes_seconds_separation.grid(pady=2, column=3, row=0, sticky='w')
        self.current_window.hours_minutes_separation.grid(padx=0, pady=2, column=1, row=0, sticky='e')

        self.current_window.timer_counter_label.grid_forget()

        for stringvar, val in stringvars:
            self.current_window.after(0, lambda stringvar=stringvar, val=val: stringvar.set(val))
            
        for entry in self.current_window.entries:
            self.current_window.after(0, lambda entry=entry: entry.configure(text_color='gray'))
        
    def start_stopwatch(self):
        if self.is_stopwatch_running:
            return
        
        self.is_stopwatch_running = True
        self.current_window.stopwatch_stop.configure(state='normal')
        self.current_window.stopwatch_start.configure(state='disabled')
        self.current_window.stopwatch_reset.configure(state='normal')
        self.last_iteration = time.perf_counter()
        
        def loop():
            if self.is_stopwatch_running:
                current_iteration = time.perf_counter()
                delta_time = current_iteration - self.last_iteration
                self.last_iteration = current_iteration
                
                self.stopwatch_model.receive_time_units(delta_time)
                
                self.current_window.after(0, lambda: self.current_window.stopwatch_counter_stringvar.set(self.stopwatch_model.process_time()))
                
                self.root.after(10, loop)
            
        loop()
    
    def stop_stopwatch(self):
        if self.is_stopwatch_running:
            self.is_stopwatch_running = False
        self.current_window.stopwatch_stop.configure(state='disabled')
        self.current_window.stopwatch_start.configure(state='normal')
    
    def reset_stopwatch(self):
        self.stop_stopwatch()
        self.current_window.stopwatch_reset.configure(state='disabled')
        self.stopwatch_model.reset_time_units()
        self.current_window.after(0, lambda: self.current_window.stopwatch_counter_stringvar.set("00:00:00.00"))
        
    def withdraw_current(self):
        if self.current_window is not None:
            self.current_window.withdraw()
            self.current_window = None
            
    def show_window(self, window_class):
        self.withdraw_current()
        self.current_window = window_class(self)
        self.current_window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.current_window.bind("<Button-1>", lambda e: e.widget.focus())
        
    def show_stopwatch(self):
        if self.previous_window is not self.current_window:
            self.stop_timer()
            self.show_previous()
        else:
            self.previous_window = self.current_window
            self.show_window(StopwatchView)
    
    def show_timer(self):
        self.stop_stopwatch()
        if self.previous_window is not self.current_window:
            self.show_previous()
        else:
            self.previous_window = self.current_window
            self.show_window(TimerView)

    def show_updating_window(self):
        if hasattr(self.current_window, 'stopwatch_label'):
            self.stop_stopwatch()
        if hasattr(self.current_window, 'timer_label'):
            self.stop_timer()
            
        self.withdraw_current()
        self.current_window = UpdatingView(self)

    def show_previous(self):
        self.withdraw_current()
        self.current_window = self.previous_window
        self.previous_window.deiconify()
        
    def on_close(self):
            self.current_window.destroy()
            self.root.destroy()

    def close_and_rename(self):
        if isLinux():
            new_file = 'Kronos-x86_64-NEW.AppImage'
            file_name = 'Kronos-x86_64.AppImage'
            
            cmd = ['sh', '-c', f'(sleep 1; mv "{new_file}" "{file_name}"; chmod +x "{file_name}"; exec "{os.path.abspath(file_name)}") >/dev/null 2>&1']
            
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True)
            os._exit(0)
        else:
            cwd = self.get_app_dir()
            
            new_file = 'Kronos-NEW.exe'
            file_name = 'Kronos.exe'
            
            new_file_abs = os.path.join(cwd, new_file)
            file_name_abs = os.path.join(cwd, file_name)
            
            os.system(f'start /b cmd /c "timeout /nobreak > nul 2 & move /y "{new_file_abs}" "{file_name_abs}" >nul 2>&1 &"')
            os._exit(0)
            os.system('exit')
            
        if self.current_window is not None:
            self.current_window.destroy()
        self.root.destroy()
        sys.exit()

class StopwatchView(ctk.CTkToplevel):  # contains UI
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
        self.title("Kronos")
        dynamic_resolution(self, 450, 250)
        self.resizable(False, False)
        self.after(200, lambda: set_window_icon(self))

        self.stopwatch_label = ctk.CTkLabel(self, font=("", 40), text="Stopwatch")
        self.stopwatch_label.pack(pady=15)
        
        self.stopwatch_counter_frame = ctk.CTkFrame(self, height=50, border_width=1, corner_radius=20)
        self.stopwatch_counter_frame.pack(anchor="center", fill='x', padx=100)

        self.stopwatch_counter_stringvar = ctk.StringVar(value="00:00:00.00")
        self.stopwatch_counter_label = ctk.CTkLabel(self.stopwatch_counter_frame, font=("", 28), textvariable=self.stopwatch_counter_stringvar)
        self.stopwatch_counter_label.pack(padx=2, pady=2)
        
        self.stopwatch_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stopwatch_button_frame.rowconfigure(0, weight=1)
        self.stopwatch_button_frame.columnconfigure((0,1,2), weight=1)
        self.stopwatch_button_frame.pack(pady=15)
        
        self.stopwatch_start = ctk.CTkButton(self.stopwatch_button_frame, font=("", 20), text="Start", width=80, corner_radius=10, command=self.controller.start_stopwatch, fg_color="#950808", hover_color="#630202", border_color="#440000", border_width=1)
        self.stopwatch_start.grid(row=0, column=1, sticky="nsew", padx=5)
    
        self.stopwatch_stop = ctk.CTkButton(self.stopwatch_button_frame, font=("", 20), text="Stop", width=80, corner_radius=10, command=self.controller.stop_stopwatch, fg_color="#950808", hover_color="#630202", border_color="#440000", border_width=1)
        self.stopwatch_stop.configure(state="disabled")
        self.stopwatch_stop.grid(row=0, column=0, sticky="nsew")
        
        self.stopwatch_reset = ctk.CTkButton(self.stopwatch_button_frame, font=("", 20), text="Reset", width=80, corner_radius=10, command=self.controller.reset_stopwatch, state='disabled', fg_color="#950808", hover_color="#630202", border_color="#440000", border_width=1)
        self.stopwatch_reset.grid(row=0, column=2, sticky="nsew")
        
        self.window_swap_frame = ctk.CTkFrame(self, width=80, border_width=1, corner_radius=50)
        self.window_swap_frame.rowconfigure(0, weight=1)
        self.window_swap_frame.columnconfigure((0,1), weight=1)
        self.window_swap_frame.pack(anchor="se", pady=15, padx=(0,10))
        
        self.swap_stopwatch_button = ctk.CTkButton(self.window_swap_frame, font=("", 13), text="Stopwatch", width=100, corner_radius=2, fg_color="gray", border_width=1)
        self.swap_stopwatch_button.configure(state="disabled")
        self.swap_stopwatch_button.grid(row=0, column=0, sticky="nsew")
        
        self.swap_timer_button = ctk.CTkButton(self.window_swap_frame, font=("", 13), text="Timer", width=100, corner_radius=2, command=self.controller.show_timer, fg_color="#950808", hover_color="#630202", border_color="#440000", border_width=1)
        self.swap_timer_button.grid(row=0, column=1, sticky="nsew")
    
class TimerView(ctk.CTkToplevel):  # contains UI
    FOCUS_IN = "<FocusIn>"
    FOCUS_OUT = "<FocusOut>"
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
        self.title("Kronos")
        dynamic_resolution(self, 450, 250)
        self.resizable(False, False)
        self.after(200, lambda: set_window_icon(self))
        
        self.timer_label = ctk.CTkLabel(self, font=("", 40), text="Timer")
        self.timer_label.pack(pady=15)
        
        self.timer_counter_frame = ctk.CTkFrame(self, height=50, border_width=1, corner_radius=20)
        self.timer_counter_frame.rowconfigure(0, weight=1)
        self.timer_counter_frame.columnconfigure(0, weight=1)
        self.timer_counter_frame.columnconfigure(1, weight=0)
        self.timer_counter_frame.columnconfigure(2, weight=1)
        self.timer_counter_frame.columnconfigure(3, weight=0)
        self.timer_counter_frame.columnconfigure(4, weight=1)
        self.timer_counter_frame.pack(anchor="center", fill='x', padx=100)
        
        self.timer_counter_label_strvar = ctk.StringVar(value="")
        self.timer_counter_label = ctk.CTkLabel(self.timer_counter_frame, font=("", 28), fg_color="transparent", bg_color="transparent", textvariable=self.timer_counter_label_strvar)

        self.timer_hours_stringvar = ctk.StringVar()
        self.timer_counter_hours = ctk.CTkEntry(self.timer_counter_frame, font=("", 25), fg_color="transparent", bg_color="transparent", border_width=1, width=20, placeholder_text='h', justify="center", text_color='gray', textvariable=self.timer_hours_stringvar)
        self.timer_counter_hours.insert(0, 'h')
        self.timer_counter_hours.grid(padx=(20, 10), pady=2, column=0, row=0, sticky='nsew')
        self.timer_counter_hours.bind(TimerView.FOCUS_IN, self.timer_hours_handler_in)
        self.timer_counter_hours.bind(TimerView.FOCUS_OUT, self.timer_hours_handler_out)
        
        self.hours_minutes_separation = ctk.CTkLabel(self.timer_counter_frame, font=("", 25), text=":")
        self.hours_minutes_separation.grid(padx=0, pady=2, column=1, row=0, sticky='e')
        
        self.timer_minutes_stringvar = ctk.StringVar()
        self.timer_counter_minutes = ctk.CTkEntry(self.timer_counter_frame, font=("", 25), fg_color="transparent", bg_color="transparent", border_width=1, width=20, placeholder_text='m', justify="center", text_color='gray', textvariable=self.timer_minutes_stringvar)
        self.timer_counter_minutes.insert(0, 'm')
        self.timer_counter_minutes.grid(padx=15, pady=2, column=2, row=0, sticky='nsew')
        self.timer_counter_minutes.bind(TimerView.FOCUS_IN, self.timer_minutes_handler_in)
        self.timer_counter_minutes.bind(TimerView.FOCUS_OUT, self.timer_minutes_handler_out)
        
        self.minutes_seconds_separation = ctk.CTkLabel(self.timer_counter_frame, font=("", 25), text=":")
        self.minutes_seconds_separation.grid(pady=2, column=3, row=0, sticky='w')
        
        self.timer_seconds_stringvar = ctk.StringVar()
        self.timer_counter_seconds = ctk.CTkEntry(self.timer_counter_frame, font=("", 25), fg_color="transparent", bg_color="transparent", border_width=1, width=20, placeholder_text='s', justify="center", text_color='gray', textvariable=self.timer_seconds_stringvar)
        self.timer_counter_seconds.insert(0, 's')
        self.timer_counter_seconds.grid(padx=(10, 20), pady=2, column=4, row=0, sticky='nsew')
        self.timer_counter_seconds.bind(TimerView.FOCUS_IN, self.timer_seconds_handler_in)
        self.timer_counter_seconds.bind(TimerView.FOCUS_OUT, self.timer_seconds_handler_out)
        
        self.timer_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.timer_button_frame.rowconfigure(0, weight=1)
        self.timer_button_frame.columnconfigure((0,1,2), weight=1)
        self.timer_button_frame.pack(pady=15)
        
        self.timer_start = ctk.CTkButton(self.timer_button_frame, font=("", 20), text="Start", width=80, corner_radius=10, command=self.controller.start_timer, fg_color="#950808", hover_color="#630202", border_color="#440000", border_width=1)
        self.timer_start.grid(row=0, column=1, sticky="nsew", padx=5)
    
        self.timer_stop = ctk.CTkButton(self.timer_button_frame, font=("", 20), text="Stop", width=80, corner_radius=10, state="disabled", command=self.controller.stop_timer, fg_color="#950808", hover_color="#630202", border_color="#440000", border_width=1)
        self.timer_stop.grid(row=0, column=0, sticky="nsew")
        
        self.timer_reset = ctk.CTkButton(self.timer_button_frame, font=("", 20), text="Reset", width=80, corner_radius=10, state='disabled', command=self.controller.reset_timer, fg_color="#950808", hover_color="#630202", border_color="#440000", border_width=1)
        self.timer_reset.grid(row=0, column=2, sticky="nsew")
        
        self.window_swap_frame = ctk.CTkFrame(self, width=80, border_width=1, corner_radius=50)
        self.window_swap_frame.rowconfigure(0, weight=1)
        self.window_swap_frame.columnconfigure((0,1), weight=1)
        self.window_swap_frame.pack(anchor="se", pady=15, padx=(0,10))
        
        self.swap_stopwatch_button = ctk.CTkButton(self.window_swap_frame, font=("", 13), text="Stopwatch", width=100, corner_radius=2, command=self.controller.show_stopwatch, fg_color="#950808", hover_color="#630202", border_color="#440000", border_width=1)
        self.swap_stopwatch_button.grid(row=0, column=0, sticky="nsew")
        
        self.swap_timer_button = ctk.CTkButton(self.window_swap_frame, font=("", 13), text="Timer", width=100, corner_radius=2, state="disabled", fg_color="gray", border_width=1)
        self.swap_timer_button.grid(row=0, column=1, sticky="nsew")
        
        self.entries = [(self.timer_counter_hours), (self.timer_counter_minutes), (self.timer_counter_seconds)]
        
    def timer_hours_handler_in(self, event):
        if self.timer_counter_hours.get() == 'h':
            self.timer_counter_hours.delete(0, ctk.END)
            self.timer_counter_hours.configure(text_color='white')
                
    def timer_minutes_handler_in(self, event):
        if self.timer_counter_minutes.get() == 'm':
            self.timer_counter_minutes.delete(0, ctk.END)
            self.timer_counter_minutes.configure(text_color='white')
        
    def timer_seconds_handler_in(self, event):
        if self.timer_counter_seconds.get() == 's':
            self.timer_counter_seconds.delete(0, ctk.END)
            self.timer_counter_seconds.configure(text_color='white')
        
    def timer_hours_handler_out(self, event):
        if self.timer_counter_hours.get().strip() == '':
            self.timer_counter_hours.configure(text_color='gray')
            self.timer_counter_hours.insert(0, 'h')

    def timer_minutes_handler_out(self, event):
        if self.timer_counter_minutes.get().strip() == '':
            self.timer_counter_minutes.configure(text_color='gray')
            self.timer_counter_minutes.insert(0, 'm')

    def timer_seconds_handler_out(self, event):
        if self.timer_counter_seconds.get().strip() == '':
            self.timer_counter_seconds.configure(text_color='gray')
            self.timer_counter_seconds.insert(0, 's')

class UpdatingView(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        
        set_window_icon(self)
        dynamic_resolution(self, 450, 100)
        self.resizable(False, False)
        self.title('Updating...')
        self.bind("<Button-1>", lambda e: e.widget.focus())
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.progress_label1 = ctk.CTkLabel(self, text="Update in progress.", font=("", 20))
        self.progress_label1.pack()
        
        self.progress_label2 = ctk.CTkLabel(self, text="Please, don't close this window while the application is being updated.", font=("", 12))
        self.progress_label2.pack()
        
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", height=10, width=400, corner_radius=10, progress_color="#770505", fg_color="#808080", mode="indeterminate", border_color="#1d0000", border_width=1)
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()
        
    def on_closing(self):
        self.destroy()
        self.app.root.destroy()

class StopwatchModel:  # contains logic independently
    def __init__(self):
        self.time_units = 0
    
    def receive_time_units(self, value):
        self.time_units += value
        
    def reset_time_units(self):
        if self.time_units != 0:
            self.time_units = 0
    
    def process_time(self):
        seconds = int(self.time_units)
        centiseconds = int((self.time_units - seconds) * 100) % 100
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}.{centiseconds:02}"

class TimerModel:  # contains logic independently
    def __init__(self):
        self.remaining_time = 0
        self.timer_hour = 0
        self.timer_min = 0
        self.timer_sec = 0
        
    def receive_timer_counter(self, hour, minutes, sec):
        self.timer_hour = hour
        self.timer_min = minutes
        self.timer_sec = sec +1
        self.remaining_time = self.timer_hour * 3600 + self.timer_min * 60 + self.timer_sec

    def timer_process_time(self):
        total_seconds = max(int(self.remaining_time), 0)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    def get_remaining_time(self):
        return self.remaining_time
    
    def detract_remaining_time(self, value):
        if value > 0:
            self.remaining_time -= value
            if self.remaining_time < 0:
                self.remaining_time = 0
    
if __name__ == "__main__":
    main()
