import tkinter as tk
from tkinter import ttk, messagebox
import threading
import schedule
import time
from datetime import datetime
from main import main as mainF
from logger_execution import read_log, return_all_log_files, read_log_by_filename


class CalendarNotifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Calendar Notifier")
        self.root.geometry("480x420")
        self.root.resizable(False, False)
        self.root.configure(bg="#1E1E1E")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", background="#1E1E1E", foreground="white", font=("Segoe UI", 11))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        self.style.map("TButton", background=[("active", "#0078D4")], foreground=[("active", "white")])

        ttk.Label(root, text="WhatsApp Calendar Notifier", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Orario
        frame_time = ttk.Frame(root)
        frame_time.pack(pady=10)
        ttk.Label(frame_time, text="Orario di notifica (HH:MM):").grid(row=0, column=0, padx=5)
        self.time_entry = ttk.Entry(frame_time, width=10)
        self.time_entry.insert(0, "07:00")
        self.time_entry.grid(row=0, column=1, padx=5)

        # Pulsanti principali
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="▶️ Avvia Servizio", command=self.start_service).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="⏹️ Ferma Servizio", command=self.stop_service).grid(row=0, column=1, padx=10)
        ttk.Button(btn_frame, text="📜 Mostra Log", command=self.show_log).grid(row=0, column=2, padx=10)

        # Pulsante "Esegui ora"
        ttk.Button(root, text="⚡ Esegui ora", command=self.run_now).pack(pady=10)

        self.status_label = ttk.Label(root, text="Stato: Inattivo", foreground="gray")
        self.status_label.pack(pady=10)

        self.running = False

    def start_service(self):
        time_str = self.time_entry.get().strip()
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Errore", "Formato orario non valido (usa HH:MM)")
            return

        schedule.clear()
        schedule.every().day.at(time_str).do(mainF)

        self.running = True
        threading.Thread(target=self.scheduler_loop, daemon=True).start()
        self.status_label.config(text=f"Stato: Attivo ({time_str})", foreground="#4CAF50")

    def stop_service(self):
        self.running = False
        schedule.clear()
        self.status_label.config(text="Stato: Inattivo", foreground="gray")

    def scheduler_loop(self):
        while self.running:
            schedule.run_pending()
            time.sleep(30)

    def show_log_windows(self, filename):
        try:
            log_data = read_log_by_filename(filename)
        except FileNotFoundError:
            log_data = "Nessun log disponibile."

        log_window = tk.Toplevel(self.root)
        log_window.title(f"Log: {filename}")
        log_window.geometry("800x600")
        text_widget = tk.Text(log_window, wrap="word", bg="#2D2D2D", fg="white", font=("Consolas", 10))
        text_widget.insert("1.0", log_data)
        text_widget.config(state="disabled")
        text_widget.pack(expand=True, fill="both")

    def show_log(self):
        log_files = return_all_log_files()

        # Crea la finestra
        log_window = tk.Toplevel(self.root)
        log_window.title("Log disponibili")
        log_window.geometry("500x500")
        log_window.configure(bg="#1E1E1E")

        # Se non ci sono log
        if not log_files:
            ttk.Label(
                log_window,
                text="📂 Nessun log disponibile",
                font=("Segoe UI", 11, "bold")
            ).pack(pady=20)
            return

        # Titolo se ci sono log
        ttk.Label(
            log_window,
            text="Seleziona un file di log:",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=10)

        # Frame con scrollbar per i pulsanti
        frame_logs = ttk.Frame(log_window)
        frame_logs.pack(expand=True, fill="both", padx=20, pady=10)

        canvas = tk.Canvas(frame_logs, bg="#1E1E1E", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_logs, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Crea un pulsante per ogni file di log
        for log in log_files:
            ttk.Button(
                scroll_frame,
                text=log,
                command=lambda l=log: self.show_log_windows(l)
            ).pack(pady=4, fill="x", padx=10)

    def run_now(self):
        try:
            mainF()
            messagebox.showinfo("Eseguito", "Reminder eseguito con successo!")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esecuzione: {e}")

def main():
    root = tk.Tk()
    app = CalendarNotifierApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
