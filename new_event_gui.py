import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import threading
from create_event import send_event_to_calendar
from logger_execution import write_log


class CalendarEventGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 Nuovo Evento – Windows 11")
        self.center_window(480, 560)
        self.root.configure(bg="#ebecf0")

        # Ombra esterna simulata
        shadow = tk.Frame(root, bg="#d0d2d6", bd=0)
        shadow.place(relx=0.5, rely=0.5, anchor="center", width=440, height=520)

        # Card principale
        self.card = tk.Frame(root, bg="#ffffff", bd=0, relief="flat",
                             highlightthickness=1, highlightbackground="#d6d6d6")
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=440, height=520)

        # Tema Fluent / Segoe UI Variable
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#ffffff", foreground="#1a1a1a",
                        font=("Segoe UI Variable", 10))
        style.configure("TButton", font=("Segoe UI Variable Display", 10, "bold"),
                        padding=8, relief="flat")
        style.configure("Accent.TButton",
                        background="#0078D4",
                        foreground="white",
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor="#005A9E")
        style.map("Accent.TButton",
                  background=[("active", "#005A9E"), ("pressed", "#004B87")])
        style.configure("TEntry", fieldbackground="#f8f8f8", borderwidth=1, relief="flat")
        style.configure("TCombobox", fieldbackground="#f8f8f8", arrowsize=15)

        # Titolo header
        tk.Label(self.card, text="🗓️ Crea un nuovo evento",
                 bg="#ffffff", fg="#0078D4",
                 font=("Segoe UI Variable Display", 14, "bold")).pack(pady=18)

        # ---- CAMPI FORM ----
        self.create_labeled_entry("Titolo evento", "title_entry")
        self.create_labeled_text("Descrizione", "desc_entry")

        self.create_date_time_inputs("Inizio", "start")
        self.create_date_time_inputs("Fine", "end")

        # Loader (nascosto)
        self.loader = ttk.Label(self.card, text="⏳ Invio in corso...",
                                foreground="#0078D4", background="#ffffff",
                                font=("Segoe UI Variable", 10, "italic"))
        self.loader.pack(pady=10)
        self.loader.pack_forget()

        # Bottone principale
        self.btn_create = ttk.Button(self.card, text="Crea Evento",
                                     style="Accent.TButton", command=self.start_create_event)
        self.btn_create.pack(pady=20)

    # ====== UI HELPERS ======
    def create_labeled_entry(self, label, attr):
        ttk.Label(self.card, text=label).pack(anchor="w", padx=40)
        entry = ttk.Entry(self.card, width=42)
        entry.pack(pady=6)
        setattr(self, attr, entry)

    def create_labeled_text(self, label, attr):
        ttk.Label(self.card, text=label).pack(anchor="w", padx=40)
        text = tk.Text(self.card, height=4, width=42, bg="#f8f8f8", bd=0,
                       highlightthickness=1, highlightbackground="#dcdcdc",
                       font=("Segoe UI Variable", 10))
        text.pack(pady=6)
        setattr(self, attr, text)

    def create_date_time_inputs(self, label_prefix, attr_prefix):
        ttk.Label(self.card, text=f"Data {label_prefix.lower()}").pack(anchor="w", padx=40)
        date = DateEntry(self.card, width=18, background="#0078D4",
                         foreground="white", borderwidth=0,
                         date_pattern="yyyy-mm-dd")
        date.pack(pady=3)
        ttk.Label(self.card, text=f"Ora {label_prefix.lower()} (HH:MM)").pack(anchor="w", padx=40)
        time = ttk.Entry(self.card, width=10)
        time.insert(0, "09:00" if "start" in attr_prefix else "10:00")
        time.pack(pady=3)
        setattr(self, f"{attr_prefix}_date", date)
        setattr(self, f"{attr_prefix}_time", time)

    # ====== FUNZIONI DI SUPPORTO ======
    def center_window(self, width, height):
        """Centra la finestra sullo schermo"""
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = int((screen_w / 2) - (width / 2))
        y = int((screen_h / 2) - (height / 2))
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # ====== THREADING + LOGICA ======
    def start_create_event(self):
        self.disable_form()
        self.loader.pack()
        threading.Thread(target=self.create_event, daemon=True).start()

    def create_event(self):
        try:
            title = self.title_entry.get().strip()
            desc = self.desc_entry.get("1.0", "end").strip()
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            start_time = self.start_time.get().strip()
            end_time = self.end_time.get().strip()

            if not title:
                self.show_message("Errore", "Il titolo è obbligatorio.", error=True)
                write_log("Errore", "Il titolo è obbligatorio.", error=True)
                return

            start = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            end = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")

            send_event_to_calendar(title, desc, start, end)
            self.show_message("Successo", "✅ Evento inviato con successo a Google Calendar!")
            write_log("Successo: ✅ Evento inviato con successo a Google Calendar!")

        except ValueError:
            self.show_message("Errore", "Formato ora non valido. Usa HH:MM.", error=True)
            write_log("Errore: Formato ora non valido. Usa HH:MM.")
        except Exception as e:
            self.show_message(f"Errore: Si è verificato un problema:\n{e}")
            write_log(f"Errore: Si è verificato un problema:\n{e} error=True")
        finally:
            self.enable_form()

    def disable_form(self):
        widgets = [
            self.btn_create, self.title_entry, self.desc_entry,
            self.start_time, self.end_time, self.start_date, self.end_date
        ]
        for w in widgets:
            w.config(state="disabled")

    def enable_form(self):
        widgets = [
            self.btn_create, self.title_entry, self.desc_entry,
            self.start_time, self.end_time, self.start_date, self.end_date
        ]
        for w in widgets:
            w.config(state="normal")
        self.loader.pack_forget()

    def show_message(self, title, text, error=False):
        self.root.after(0, lambda: (
            messagebox.showerror(title, text) if error else messagebox.showinfo(title, text)
        ))


def main():
    root = tk.Tk()
    app = CalendarEventGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
