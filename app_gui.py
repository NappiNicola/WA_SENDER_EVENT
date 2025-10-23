import tkinter as tk
from tkinter import ttk, messagebox
import threading, schedule, time
from datetime import datetime
from main import main as mainF
from logger_execution import read_log_by_filename, return_all_log_files
from new_event_gui import main as new_event_window

class CalendarNotifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 WhatsApp Calendar Notifier")

        # === Dimensione e centramento ===
        w, h = 480, 440
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        x, y = int((sw - w) / 2), int((sh - h) / 2)
        root.geometry(f"{w}x{h}+{x}+{y}")
        root.resizable(False, False)

        # === Tavolozza colori stile Windows 11 ===
        self.bg_main = "#ebecf0"
        self.bg_panel = "#ffffff"
        self.shadow = "#d0d2d6"
        self.fg_text = "#1e1e1e"
        self.fg_subtle = "#555555"
        self.accent = "#0078d4"
        self.accent_hover = "#1890f1"
        self.entry_bg = "#f5f6f8"
        self.loader_bg = "#ebecf0"

        root.configure(bg=self.bg_main)
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.bg_main)
        style.configure("TLabel", background=self.bg_main, foreground=self.fg_text, font=("Segoe UI Variable", 10))
        style.configure("TEntry", fieldbackground=self.bg_panel, foreground=self.fg_text, insertcolor=self.fg_text)
        style.configure("Accent.TButton",
                        background=self.accent, foreground="white",
                        font=("Segoe UI Variable", 10, "bold"),
                        padding=8, relief="flat")
        style.map("Accent.TButton", background=[("active", self.accent_hover)])

        # === Titolo ===
        ttk.Label(root, text="WhatsApp Calendar Notifier",
                  font=("Segoe UI Variable", 16, "bold"),
                  foreground=self.accent,
                  background=self.bg_main).pack(pady=(20, 10))

        ttk.Separator(root, orient="horizontal").pack(fill="x", padx=25, pady=10)

        # === Sezione orario ===
        frame_time = ttk.Frame(root)
        frame_time.pack(pady=10)
        ttk.Label(frame_time, text="Orario di notifica (HH:MM):").grid(row=0, column=0, padx=5)
        self.time_entry = ttk.Entry(frame_time, width=10)
        self.time_entry.insert(0, "07:00")
        self.time_entry.grid(row=0, column=1, padx=5)

        # === Pulsanti principali ===
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=15)

        self.create_modern_button(btn_frame, "▶️ Avvia Servizio", self.start_service_thread, 0)
        self.create_modern_button(btn_frame, "⏹️ Ferma Servizio", self.stop_service, 1)
        self.create_modern_button(btn_frame, "📜 Mostra Log", self.show_log, 2)

        self.create_modern_button(root, "⚡ Esegui ora", self.run_now).pack(pady=10)
        self.create_modern_button(root, "🗓️ Nuovo Evento", new_event_window).pack(pady=10)

        self.status_label = ttk.Label(root, text="Stato: Inattivo", foreground=self.fg_subtle, background=self.bg_main)
        self.status_label.pack(pady=15)

        self.running = False

    # ====================== COMPONENTI ======================
    def create_modern_button(self, parent, text, command, column=None):
        """Crea un pulsante moderno stile Windows 11"""
        btn = tk.Label(parent, text=text, bg=self.accent, fg="white",
                       font=("Segoe UI Variable", 10, "bold"), padx=12, pady=8,
                       cursor="hand2", relief="flat", bd=0)
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.config(bg=self.accent_hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.accent))
        if column is not None:
            btn.grid(row=0, column=column, padx=10)
        else:
            return btn

    # ====================== LOADER ======================
    def show_loader(self, message="Caricamento in corso..."):
        """Mostra loader in stile Windows 11"""
        self.loader = tk.Toplevel(self.root)
        self.loader.overrideredirect(True)
        self.loader.attributes("-topmost", True)
        self.loader.configure(bg=self.bg_panel)
        self.center_window(self.loader, 300, 140)

        ttk.Label(self.loader, text=message, font=("Segoe UI Variable", 11, "bold"),
                  background=self.bg_panel, foreground=self.fg_text).pack(pady=(25, 15))

        self.progress = ttk.Progressbar(self.loader, mode="indeterminate", length=200)
        self.progress.pack(pady=(5, 10))
        self.progress.start(10)

    def hide_loader(self):
        if hasattr(self, "loader"):
            self.progress.stop()
            self.loader.destroy()

    # ====================== SERVIZIO ======================
    def start_service_thread(self):
        threading.Thread(target=self._start_service_logic, daemon=True).start()

    def _start_service_logic(self):
        self.show_loader("⏳ Avvio del servizio...")
        try:
            time_str = self.time_entry.get().strip()
            datetime.strptime(time_str, "%H:%M")
            schedule.clear()
            schedule.every().day.at(time_str).do(mainF)
            self.running = True
            threading.Thread(target=self.scheduler_loop, daemon=True).start()
            self.status_label.config(text=f"Stato: Attivo ({time_str})", foreground="#4CAF50")
            time.sleep(1.5)
        except ValueError:
            self.hide_loader()
            messagebox.showerror("Errore", "Formato orario non valido (usa HH:MM)")
            return
        finally:
            self.hide_loader()

    def stop_service(self):
        self.running = False
        schedule.clear()
        self.status_label.config(text="Stato: Inattivo", foreground=self.fg_subtle)

    def scheduler_loop(self):
        while self.running:
            schedule.run_pending()
            time.sleep(30)

    # ====================== LOG ======================
    def show_log_windows(self, filename):
        try:
            log_data = read_log_by_filename(filename)
        except FileNotFoundError:
            log_data = "Nessun log disponibile."

        log_window = tk.Toplevel(self.root)
        log_window.title(f"Log: {filename}")
        log_window.configure(bg=self.bg_main)
        self.center_window(log_window, 800, 600)

        text_widget = tk.Text(log_window, wrap="word", bg=self.bg_panel,
                              fg=self.fg_text, font=("Consolas", 10), bd=0, relief="flat")
        text_widget.insert("1.0", log_data)
        text_widget.config(state="disabled")
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

    def show_log(self):
        log_files = return_all_log_files()
        log_window = tk.Toplevel(self.root)
        log_window.title("Log disponibili")
        log_window.configure(bg=self.bg_main)
        self.center_window(log_window, 500, 500)

        if not log_files:
            ttk.Label(log_window, text="📂 Nessun log disponibile",
                      font=("Segoe UI Variable", 11, "bold"), background=self.bg_main,
                      foreground=self.fg_text).pack(pady=20)
            return

        ttk.Label(log_window, text="Seleziona un file di log:",
                  font=("Segoe UI Variable", 11, "bold"), background=self.bg_main,
                  foreground=self.fg_text).pack(pady=10)

        frame_logs = ttk.Frame(log_window)
        frame_logs.pack(expand=True, fill="both", padx=20, pady=10)

        canvas = tk.Canvas(frame_logs, bg=self.bg_main, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(frame_logs, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="TFrame")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for log in log_files:
            self.create_modern_button(scroll_frame, log, lambda l=log: self.show_log_windows(l)).pack(pady=4, fill="x", padx=10)

    # ====================== ESECUZIONE ======================
    def run_now(self):
        # threading.Thread(target=self._run_now_thread, daemon=True).start()
        try:
            mainF()
            time.sleep(1)
            messagebox.showinfo("Eseguito", "✅ Reminder eseguito con successo!")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esecuzione: {e}")

    def _run_now_thread(self):
        self.show_loader("⚙️ Esecuzione in corso...")
        try:
            mainF()
            time.sleep(1)
            self.hide_loader()
            messagebox.showinfo("Eseguito", "✅ Reminder eseguito con successo!")
        except Exception as e:
            self.hide_loader()
            messagebox.showerror("Errore", f"Errore durante l'esecuzione: {e}")

    # ====================== UTILS ======================
    def center_window(self, window, width, height):
        window.update_idletasks()
        sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()
        x, y = int((sw - width) / 2), int((sh - height) / 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

def main():
    root = tk.Tk()
    app = CalendarNotifierApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
