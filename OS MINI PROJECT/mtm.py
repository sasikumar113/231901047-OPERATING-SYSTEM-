import tkinter as tk
from tkinter import ttk, messagebox
import psutil
from graph import plot_cpu_usage_all

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Task Manager with Checkboxes & Graph")
        self.root.geometry("900x500")
        self.seen_pids = set()
        self.checked_pids = set()

        # Treeview Setup
        self.tree = ttk.Treeview(root, columns=("Checkbox", "Name", "PID", "State"), show="headings")
        self.tree.heading("Checkbox", text="")
        self.tree.heading("Name", text="Application")
        self.tree.heading("PID", text="PID")
        self.tree.heading("State", text="State")

        self.tree.column("Checkbox", width=60, anchor='center')
        self.tree.column("Name", width=350)
        self.tree.column("PID", width=100)
        self.tree.column("State", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree.bind("<Button-1>", self.on_tree_click)

        # Button Frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        terminate_btn = tk.Button(button_frame, text="Terminate Selected Process", command=self.terminate_process)
        terminate_btn.pack(side=tk.LEFT, padx=10)

        refresh_btn = tk.Button(button_frame, text="Refresh", command=self.refresh_process_list)
        refresh_btn.pack(side=tk.LEFT, padx=10)

        graph_btn = tk.Button(button_frame, text="Show CPU Usage Graph", command=plot_cpu_usage_all)
        graph_btn.pack(side=tk.LEFT, padx=10)

        self.update_process_list()

    def get_process_state(self, proc):
        try:
            status = proc.status()
            pid = proc.pid
            if pid not in self.seen_pids:
                self.seen_pids.add(pid)
                return "new"
            elif status == psutil.STATUS_RUNNING:
                return "running"
            elif status in [psutil.STATUS_SLEEPING, psutil.STATUS_WAITING]:
                return "waiting"
            elif status in [psutil.STATUS_ZOMBIE, psutil.STATUS_STOPPED, psutil.STATUS_DEAD]:
                return "terminated"
            elif status == psutil.STATUS_IDLE:
                return "idle"
            else:
                return status
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return "terminated"

    def update_process_list(self):
        current_checked = set(self.checked_pids)
        self.tree.delete(*self.tree.get_children())
        self.checked_pids.clear()

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name']
                pid = str(proc.info['pid'])
                state = self.get_process_state(proc)
                checked = pid in current_checked
                checkbox = "[x]" if checked else "[ ]"

                if checked:
                    self.checked_pids.add(pid)

                self.tree.insert("", tk.END, iid=pid, values=(checkbox, name, pid, state))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Refresh every 3 seconds
        self.root.after(3000, self.update_process_list)

    def refresh_process_list(self):
        self.update_process_list()

    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        if column != "#1":
            return

        row = self.tree.identify_row(event.y)
        if not row:
            return

        pid = self.tree.item(row, "values")[2]
        if pid in self.checked_pids:
            self.checked_pids.remove(pid)
            self.tree.set(row, column="#1", value="[ ]")
        else:
            self.checked_pids.add(pid)
            self.tree.set(row, column="#1", value="[x]")

    def terminate_process(self):
        if not self.checked_pids:
            messagebox.showwarning("No Selection", "Please check at least one process to terminate.")
            return

        for pid in self.checked_pids:
            try:
                proc = psutil.Process(int(pid))
                proc.terminate()
                messagebox.showinfo("Success", f"Process {pid} terminated.")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                messagebox.showerror("Error", f"Could not terminate process {pid}.")

# Main Tkinter Window
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
