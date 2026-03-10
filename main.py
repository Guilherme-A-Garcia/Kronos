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

class StopwatchView(ctk.CTkToplevel):  # contains UI
    def __init__(self):
        super().__init__()
    
class TimerView(ctk.CTkToplevel):  # contains UI
    def __init__(self):
        super().__init__()
        
class StopwatchModel:  # contains logic independently
    def __init__(self):
        pass

class TimerModel:  # contains logic independently
    def __init__(self):
        pass
    
if __name__ == "__main__":
    main()