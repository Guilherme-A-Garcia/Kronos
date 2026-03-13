import time
import threading
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

def main():
    app = WindowController()
    app.root.mainloop()

class WindowController:  # receives and manages views' calls and models
    def __init__(self):
        self.current_window = None
        self.stopwatch_elapsed_time = 0
        self.is_stopwatch_running = False
        
        self.root = ctk.CTk()
        self.root.withdraw()
        
        self.stopwatch_model = StopwatchModel()
        self.timer_model = TimerModel()
        
        self.show_stopwatch()
        
    def start_stopwatch(self):
        if self.is_stopwatch_running:
            return
        
        self.stopwatch_elapsed_time = 0
        self.is_stopwatch_running = True
        self.last_iteration = time.perf_counter()
        
        def loop(): # THIS LOOP IS CURRENTLY JUST SENDING DELTA TIME TO STOPWATCH MODEl FOR IT TO PROCESS IT <----
            if self.is_stopwatch_running:
                self.current_iteration = time.perf_counter()
                self.delta_time = self.current_iteration - self.last_iteration
                self.last_iteration = self.current_iteration
                
                self.stopwatch_model.receive_time_units(self.delta_time)
                
                self.root.after(10, loop)
            
        loop()
        
    def withdraw_current(self):
        if self.current_window is not None:
            self.current_window.withdraw()
            self.current_window = None
            
    def show_window(self, window_class):
        self.withdraw_current()
        self.current_window = window_class(self)
        self.current_window.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def show_stopwatch(self):
        self.show_window(StopwatchView)
    
    def show_timer(self):
        self.show_window(TimerView)
        
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

        self.stopwatch_counter_label = ctk.CTkLabel(self.stopwatch_counter_frame, font=("", 28), text="00:00:00.00")
        self.stopwatch_counter_label.pack(padx=2, pady=2)
        
        self.stopwatch_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stopwatch_button_frame.rowconfigure(0, weight=1)
        self.stopwatch_button_frame.columnconfigure((0,1,2), weight=1)
        self.stopwatch_button_frame.pack(pady=15)
        
        self.stopwatch_start = ctk.CTkButton(self.stopwatch_button_frame, font=("", 20), text="Start", width=80, corner_radius=10)
        self.stopwatch_start.grid(row=0, column=0, sticky="nsew")
    
        self.stopwatch_stop = ctk.CTkButton(self.stopwatch_button_frame, font=("", 20), text="Stop", width=80, corner_radius=10)
        self.stopwatch_stop.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.stopwatch_reset = ctk.CTkButton(self.stopwatch_button_frame, font=("", 20), text="Reset", width=80, corner_radius=10)
        self.stopwatch_reset.grid(row=0, column=2, sticky="nsew")
        
        self.stopwatch_swap_frame = ctk.CTkFrame(self, width=80, border_width=1, corner_radius=50)
        self.stopwatch_swap_frame.rowconfigure(0, weight=1)
        self.stopwatch_swap_frame.columnconfigure((0,1), weight=1)
        self.stopwatch_swap_frame.pack(anchor="se", pady=15, padx=(0,10))
        
        self.swap_stopwatch_button = ctk.CTkButton(self.stopwatch_swap_frame, font=("", 13), text="Stopwatch", width=100, corner_radius=2, fg_color="gray")
        self.swap_stopwatch_button.configure(state="disabled")
        self.swap_stopwatch_button.grid(row=0, column=0, sticky="nsew")
        
        self.swap_timer_button = ctk.CTkButton(self.stopwatch_swap_frame, font=("", 13), text="Timer", width=100, corner_radius=2)
        self.swap_timer_button.grid(row=0, column=1, sticky="nsew")
    
class TimerView(ctk.CTkToplevel):  # contains UI
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
        self.title("Kronos")
        self.geometry("450x300")
        self.resizable(False, False)
        
class StopwatchModel:  # contains logic independently
    def __init__(self):
        self.time_units = 0
    
    def receive_time_units(self, value):
        self.time_units = value
    
    def process_time(self):
        pass
        
    
    # use f"{variable:02}" for 2 character minimum padding and 0 as padding
    # come up with a way to count the ms and use divmod to divide it and store the tuple values in two variables 
    # (e.g.: divide by 1000 storing in seconds and ms)

class TimerModel:  # contains logic independently
    def __init__(self):
        pass
    
if __name__ == "__main__":
    main()
