import time
import threading
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

def main():
    app = WindowController()
    app.root.mainloop()

def err_msg(master, msg):
    error = CTkMessagebox(master=master, icon='cancel', message=msg)
    error.get()

class WindowController:  # receives and manages views' calls and models
    def __init__(self):
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
        
    def show_previous(self):
        self.withdraw_current()
        self.current_window = self.previous_window
        self.previous_window.deiconify()
        
    def on_close(self):
            self.current_window.destroy()
            self.root.destroy()

class StopwatchView(ctk.CTkToplevel):  # contains UI
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
        self.title("Kronos")
        self.geometry("450x250")
        self.resizable(False, False)

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
        
        self.stopwatch_start = ctk.CTkButton(self.stopwatch_button_frame, font=("", 20), text="Start", width=80, corner_radius=10, command=self.controller.start_stopwatch)
        self.stopwatch_start.grid(row=0, column=1, sticky="nsew", padx=5)
    
        self.stopwatch_stop = ctk.CTkButton(self.stopwatch_button_frame, font=("", 20), text="Stop", width=80, corner_radius=10, command=self.controller.stop_stopwatch)
        self.stopwatch_stop.configure(state="disabled")
        self.stopwatch_stop.grid(row=0, column=0, sticky="nsew")
        
        self.stopwatch_reset = ctk.CTkButton(self.stopwatch_button_frame, font=("", 20), text="Reset", width=80, corner_radius=10, command=self.controller.reset_stopwatch, state='disabled')
        self.stopwatch_reset.grid(row=0, column=2, sticky="nsew")
        
        self.window_swap_frame = ctk.CTkFrame(self, width=80, border_width=1, corner_radius=50)
        self.window_swap_frame.rowconfigure(0, weight=1)
        self.window_swap_frame.columnconfigure((0,1), weight=1)
        self.window_swap_frame.pack(anchor="se", pady=15, padx=(0,10))
        
        self.swap_stopwatch_button = ctk.CTkButton(self.window_swap_frame, font=("", 13), text="Stopwatch", width=100, corner_radius=2, fg_color="gray")
        self.swap_stopwatch_button.configure(state="disabled")
        self.swap_stopwatch_button.grid(row=0, column=0, sticky="nsew")
        
        self.swap_timer_button = ctk.CTkButton(self.window_swap_frame, font=("", 13), text="Timer", width=100, corner_radius=2, command=self.controller.show_timer)
        self.swap_timer_button.grid(row=0, column=1, sticky="nsew")
    
class TimerView(ctk.CTkToplevel):  # contains UI
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
        self.title("Kronos")
        self.geometry("450x250")
        self.resizable(False, False)
        
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
        self.timer_counter_hours.bind("<FocusIn>", self.timer_hours_handler_in)
        self.timer_counter_hours.bind("<FocusOut>", self.timer_hours_handler_out)
        
        self.hours_minutes_separation = ctk.CTkLabel(self.timer_counter_frame, font=("", 25), text=":")
        self.hours_minutes_separation.grid(padx=0, pady=2, column=1, row=0, sticky='e')
        
        self.timer_minutes_stringvar = ctk.StringVar()
        self.timer_counter_minutes = ctk.CTkEntry(self.timer_counter_frame, font=("", 25), fg_color="transparent", bg_color="transparent", border_width=1, width=20, placeholder_text='m', justify="center", text_color='gray', textvariable=self.timer_minutes_stringvar)
        self.timer_counter_minutes.insert(0, 'm')
        self.timer_counter_minutes.grid(padx=15, pady=2, column=2, row=0, sticky='nsew')
        self.timer_counter_minutes.bind("<FocusIn>", self.timer_minutes_handler_in)
        self.timer_counter_minutes.bind("<FocusOut>", self.timer_minutes_handler_out)
        
        self.minutes_seconds_separation = ctk.CTkLabel(self.timer_counter_frame, font=("", 25), text=":")
        self.minutes_seconds_separation.grid(pady=2, column=3, row=0, sticky='w')
        
        self.timer_seconds_stringvar = ctk.StringVar()
        self.timer_counter_seconds = ctk.CTkEntry(self.timer_counter_frame, font=("", 25), fg_color="transparent", bg_color="transparent", border_width=1, width=20, placeholder_text='s', justify="center", text_color='gray', textvariable=self.timer_seconds_stringvar)
        self.timer_counter_seconds.insert(0, 's')
        self.timer_counter_seconds.grid(padx=(10, 20), pady=2, column=4, row=0, sticky='nsew')
        self.timer_counter_seconds.bind("<FocusIn>", self.timer_seconds_handler_in)
        self.timer_counter_seconds.bind("<FocusOut>", self.timer_seconds_handler_out)
        
        self.timer_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.timer_button_frame.rowconfigure(0, weight=1)
        self.timer_button_frame.columnconfigure((0,1,2), weight=1)
        self.timer_button_frame.pack(pady=15)
        
        self.timer_start = ctk.CTkButton(self.timer_button_frame, font=("", 20), text="Start", width=80, corner_radius=10, command=self.controller.start_timer)
        self.timer_start.grid(row=0, column=1, sticky="nsew", padx=5)
    
        self.timer_stop = ctk.CTkButton(self.timer_button_frame, font=("", 20), text="Stop", width=80, corner_radius=10, state="disabled", command=self.controller.stop_timer)
        self.timer_stop.grid(row=0, column=0, sticky="nsew")
        
        self.timer_reset = ctk.CTkButton(self.timer_button_frame, font=("", 20), text="Reset", width=80, corner_radius=10, state='disabled', command=self.controller.reset_timer)
        self.timer_reset.grid(row=0, column=2, sticky="nsew")
        
        self.window_swap_frame = ctk.CTkFrame(self, width=80, border_width=1, corner_radius=50)
        self.window_swap_frame.rowconfigure(0, weight=1)
        self.window_swap_frame.columnconfigure((0,1), weight=1)
        self.window_swap_frame.pack(anchor="se", pady=15, padx=(0,10))
        
        self.swap_stopwatch_button = ctk.CTkButton(self.window_swap_frame, font=("", 13), text="Stopwatch", width=100, corner_radius=2, command=self.controller.show_stopwatch)
        self.swap_stopwatch_button.grid(row=0, column=0, sticky="nsew")
        
        self.swap_timer_button = ctk.CTkButton(self.window_swap_frame, font=("", 13), text="Timer", width=100, corner_radius=2, state="disabled", fg_color="gray")
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
