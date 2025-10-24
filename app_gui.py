import tkinter as tk
from tkinter import ttk, messagebox
import threading, schedule, time
from datetime import datetime, timedelta
from main import main as mainF
from logger_execution import read_log_by_filename, return_all_log_files
from new_event_gui import main as new_event_window


class CalendarNotifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 WhatsApp Calendar Notifier")

        # === Dimensioni e centramento ===
        w, h = 520, 540
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        x, y = int((sw - w) / 2), int((sh - h) / 2)
        root.geometry(f"{w}x{h}+{x}+{y}")
        root.resizable(False, False)

        # === Tavolozza colori professionale ===
        self.bg_main = "#f4f5f7"
        self.bg_card = "#ffffff"
        self.fg_text = "#222222"
        self.fg_muted = "#666666"
        self.accent = "#0078d7"
        self.success = "#28a745"
        self.warning = "#ffc107"
        self.border = "#d1d3d4"

        root.configure(bg=self.bg_main)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.bg_card)
        style.configure("TLabel", background=self.bg_card, foreground=self.fg_text, font=("Segoe UI", 10))
        style.configure("Accent.TButton",
                        font=("Segoe UI", 10, "bold"), padding=8, relief="flat")
        style.map("Accent.TButton",
                  background=[("active", self.accent)],
                  foreground=[("active", "white")])

        # === Card principale ===
        card = tk.Frame(root, bg=self.bg_card, highlightbackground=self.border, highlightthickness=1, bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center", width=460, height=490)

        # === Header ===
        tk.Label(card, text="📅 WhatsApp Calendar Notifier",
                 font=("Segoe UI Semibold", 15), bg=self.bg_card, fg=self.accent).pack(pady=(20, 10))

        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=20, pady=(5, 15))

        # === Orario ===
        frame_time = tk.Frame(card, bg=self.bg_card)
        frame_time.pack(pady=(5, 20))
        tk.Label(frame_time, text="⏰ Orario di notifica (HH:MM):",
                 bg=self.bg_card, fg=self.fg_text, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5)
        self.time_entry = ttk.Entry(frame_time, width=10, font=("Segoe UI", 10))
        self.time_entry.insert(0, "07:00")
        self.time_entry.grid(row=0, column=1, padx=5)

        # === Pulsanti principali ===
        btn_frame = tk.Frame(card, bg=self.bg_card)
        btn_frame.pack(pady=10)

        self.create_button(btn_frame, "▶️ Avvia Servizio", self.start_service_thread, "#0078d7", 0)
        self.create_button(btn_frame, "⏹️ Ferma Servizio", self.stop_service, "#6c757d", 1)
        self.create_button(btn_frame, "📜 Mostra Log", self.show_log, "#28a745", 2)

        # === Azioni secondarie ===
        self.create_button(card, "⚡ Esegui Ora", self.run_now, "#0dcaf0").pack(pady=(15, 6))
        self.create_button(card, "🗓️ Nuovo Evento", self.open_new_event, "#6610f2").pack(pady=(4, 20))

        # === Stato ===
        self.status_label = tk.Label(card, text="Stato: Inattivo",
                                     fg=self.fg_muted, bg=self.bg_card, font=("Segoe UI", 10, "bold"))
        self.status_label.pack(pady=(10, 0))

        # === Countdown ===
        self.countdown_label = tk.Label(card, text="Prossima esecuzione: --:--:--",
                                        fg=self.accent, bg=self.bg_card, font=("Consolas", 11, "bold"))
        self.countdown_label.pack(pady=(5, 10))

        # === Barra di progresso ===
        self.progress = ttk.Progressbar(card, mode="indeterminate", length=260)
        self.progress.pack(pady=8)

        # === Footer ===
        tk.Label(card, text="© 2025 WA Scheduler — Professional Edition",
                 font=("Segoe UI", 8), bg=self.bg_card, fg=self.fg_muted).pack(side="bottom", pady=8)

        # === Variabili ===
        self.running = False
        self.next_run_time = None

    # ====================== UI helper ======================
    def create_button(self, parent, text, command, color, column=None):
        btn = tk.Label(parent, text=text, bg=color, fg="white",
                       font=("Segoe UI", 10, "bold"), padx=14, pady=8,
                       cursor="hand2", relief="flat", bd=0)
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.config(bg=self.shade(color, -15)))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        if column is not None:
            btn.grid(row=0, column=column, padx=6, pady=4)
        else:
            return btn

    def shade(self, color, percent):
        """Schiara o scurisce un colore HEX"""
        color = color.lstrip("#")
        r, g, b = [int(color[i:i+2], 16) for i in (0, 2, 4)]
        r = max(0, min(255, r + int(r * percent / 100)))
        g = max(0, min(255, g + int(g * percent / 100)))
        b = max(0, min(255, b + int(b * percent / 100)))
        return f"#{r:02x}{g:02x}{b:02x}"

    # ====================== SERVIZIO ======================
    def start_service_thread(self):
        threading.Thread(target=self._start_service_logic, daemon=True).start()

    def _start_service_logic(self):
        try:
            time_str = self.time_entry.get().strip()
            datetime.strptime(time_str, "%H:%M")

            schedule.clear()
            schedule.every().day.at(time_str).do(mainF)
            self.running = True
            self.next_run_time = self.get_next_run_datetime(time_str)

            threading.Thread(target=self.scheduler_loop, daemon=True).start()
            self.update_countdown()

            self.progress.start(10)
            self.status_label.config(text=f"Stato: Attivo ({time_str})", fg=self.success)
        except ValueError:
            messagebox.showerror("Errore", "Formato orario non valido (usa HH:MM)")

    def stop_service(self):
        self.running = False
        schedule.clear()
        self.progress.stop()
        self.status_label.config(text="Stato: Inattivo", fg=self.fg_muted)
        self.countdown_label.config(text="Prossima esecuzione: --:--:--")

    def scheduler_loop(self):
        while self.running:
            schedule.run_pending()
            time.sleep(30)

    def get_next_run_datetime(self, time_str):
        now = datetime.now()
        target_time = datetime.strptime(time_str, "%H:%M").time()
        next_run = datetime.combine(now.date(), target_time)
        if next_run <= now:
            next_run += timedelta(days=1)
        return next_run

    def update_countdown(self):
        if not self.running or not self.next_run_time:
            return
        now = datetime.now()
        remaining = self.next_run_time - now
        if remaining.total_seconds() <= 0:
            self.next_run_time = self.get_next_run_datetime(self.time_entry.get().strip())
            remaining = self.next_run_time - now
        h, m, s = str(timedelta(seconds=int(remaining.total_seconds()))).split(":")
        self.countdown_label.config(text=f"Prossima esecuzione: {h.zfill(2)}:{m.zfill(2)}:{s.zfill(2)}")
        self.root.after(1000, self.update_countdown)

    # ====================== LOG ======================
    def show_log(self):
        log_files = return_all_log_files()
        if not log_files:
            messagebox.showinfo("Log", "Nessun log disponibile.")
            return

        log_window = tk.Toplevel(self.root)
        log_window.title("Log disponibili")
        log_window.configure(bg=self.bg_main)
        self.center_window(log_window, 500, 500)

        ttk.Label(log_window, text="Seleziona un file di log:",
                  font=("Segoe UI", 11, "bold"), background=self.bg_main,
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
            self.create_button(scroll_frame, log, lambda l=log: self.show_log_windows(l), "#0078d7").pack(pady=4, fill="x", padx=10)

        log_window.protocol("WM_DELETE_WINDOW", lambda: (log_window.destroy(), self.root.lift()))

    def show_log_windows(self, filename):
        try:
            log_data = read_log_by_filename(filename)
        except FileNotFoundError:
            log_data = "Nessun log disponibile."

        log_window = tk.Toplevel(self.root)
        log_window.title(f"Log: {filename}")
        log_window.configure(bg=self.bg_main)
        self.center_window(log_window, 800, 600)

        text_widget = tk.Text(log_window, wrap="word", bg=self.bg_card,
                              fg=self.fg_text, font=("Consolas", 10), bd=0, relief="flat")
        text_widget.insert("1.0", log_data)
        text_widget.config(state="disabled")
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        log_window.protocol("WM_DELETE_WINDOW", lambda: (log_window.destroy(), self.root.lift()))

    # ====================== ESECUZIONE ======================
    def run_now(self):
        try:
            mainF()
            messagebox.showinfo("Eseguito", "✅ Reminder eseguito con successo!")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esecuzione: {e}")

    def open_new_event(self):
        threading.Thread(target=new_event_window).start()
        # Dopo chiusura ritorna in primo piano
        self.root.after(1000, lambda: self.root.lift())

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
