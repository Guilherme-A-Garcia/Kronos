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
        self.root = ctk.CTk()
        self.root.withdraw()
        
        self.stopwatch_model = StopwatchModel()
        self.timer_model = TimerModel()
        
        self.show_stopwatch()
        
    def withdraw_current(self):
        if self.current_window is not None:
            self.current_window.destroy()

    def show_stopwatch(self):
        self.withdraw_current()
        self.current_window = StopwatchView(self)
    
    def show_timer(self):
        self.withdraw_current()
        self.current_window = TimerView(self)

class StopwatchView(ctk.CTkToplevel):  # contains UI
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
    
class TimerView(ctk.CTkToplevel):  # contains UI
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
class StopwatchModel:  # contains logic independently
    def __init__(self):
        pass

class TimerModel:  # contains logic independently
    def __init__(self):
        pass
    
if __name__ == "__main__":
    main()