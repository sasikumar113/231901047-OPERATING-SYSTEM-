import psutil
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def plot_cpu_usage_all():
    process_list = []

    # Collect CPU usage information for all processes
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Collect the CPU percentage usage
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            cpu = proc.cpu_percent(interval=None)
            name = f"{proc.info['name']} (PID {proc.info['pid']})"
            process_list.append((name, cpu))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not process_list:
        print("No process data available.")
        return

    # Sort process list by name
    process_list.sort(key=lambda x: x[0])
    names = [proc[0] for proc in process_list]
    cpu_usages = [proc[1] for proc in process_list]

    # Create a new window for displaying the plot
    window = tk.Toplevel()
    window.title("CPU Usage of All Processes")
    window.geometry("1000x600")

    # Set up the canvas and scrollbar
    frame = tk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas_frame = tk.Canvas(frame)
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=canvas_frame.xview)
    scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    canvas_frame.configure(xscrollcommand=scrollbar.set)

    plot_frame = tk.Frame(canvas_frame)
    canvas_frame.create_window((0, 0), window=plot_frame, anchor='nw')

    # Adjust the figure width based on the number of processes
    fig_width = max(10, len(names) * 0.4)
    fig = Figure(figsize=(fig_width, 6))
    ax = fig.add_subplot(111)
    ax.plot(names, cpu_usages, marker='o', linestyle='-', color='blue')

    ax.set_xlabel("Process Name (PID)")
    ax.set_ylabel("CPU Usage (%)")
    ax.set_title("CPU Usage of All Running Processes")
    ax.grid(True)
    ax.tick_params(axis='x', rotation=90)
    fig.subplots_adjust(bottom=0.3)

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

    plot_frame.update_idletasks()
    canvas_frame.config(scrollregion=canvas_frame.bbox("all"))

# Main Tkinter window
root = tk.Tk()
root.withdraw()  # Hide the root window
plot_cpu_usage_all()

root.mainloop()
