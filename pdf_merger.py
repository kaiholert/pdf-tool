"""
PDF Merger – lokale Windows-App
Abhängigkeiten: pypdf (pip install pypdf)
Packaging:      pyinstaller --onefile --windowed pdf_merger.py
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    messagebox.showerror(
        "Fehlende Bibliothek",
        "pypdf ist nicht installiert.\n\nBitte ausführen:\n  pip install pypdf",
    )
    raise SystemExit(1)


# ── Farben & Konstanten ────────────────────────────────────────────────────────
BG          = "#1e1e2e"
SURFACE     = "#2a2a3e"
SURFACE2    = "#313149"
ACCENT      = "#7c3aed"
ACCENT_HOVER= "#6d28d9"
TEXT        = "#e2e8f0"
TEXT_DIM    = "#94a3b8"
SUCCESS     = "#10b981"
DANGER      = "#ef4444"
BORDER      = "#3f3f60"
FONT_FAMILY = "Segoe UI"


class PDFMergerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Merger")
        self.geometry("820x620")
        self.minsize(680, 480)
        self.configure(bg=BG)
        self._set_icon()
        self._build_ui()
        self._drag_start = None

    # ── Icon (einfaches PDF-Symbol aus Canvas) ─────────────────────────────────
    def _set_icon(self):
        try:
            img = tk.PhotoImage(width=32, height=32)
            # Lila Hintergrund
            for y in range(32):
                for x in range(32):
                    img.put("#7c3aed", (x, y))
            self.iconphoto(True, img)
        except Exception:
            pass

    # ── UI aufbauen ────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.configure(bg=BG)

        # ── Header ────────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=SURFACE, pady=14)
        header.pack(fill="x", padx=0)

        tk.Label(
            header, text="PDF Merger", font=(FONT_FAMILY, 20, "bold"),
            bg=SURFACE, fg=TEXT,
        ).pack(side="left", padx=20)

        tk.Label(
            header,
            text="PDFs auswählen · sortieren · zusammenführen",
            font=(FONT_FAMILY, 10), bg=SURFACE, fg=TEXT_DIM,
        ).pack(side="left", padx=4, pady=6)

        # ── Hauptbereich ──────────────────────────────────────────────────────
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=18, pady=14)

        # Linke Spalte: Dateiliste
        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        list_label = tk.Label(
            left,
            text="PDF-Dateien  (Doppelklick zum Entfernen)",
            font=(FONT_FAMILY, 9), bg=BG, fg=TEXT_DIM,
        )
        list_label.pack(anchor="w", pady=(0, 4))

        # Listbox mit Scrollbar
        list_frame = tk.Frame(left, bg=BORDER, bd=1)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg=SURFACE2, troughcolor=SURFACE)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg=SURFACE, fg=TEXT,
            selectbackground=ACCENT, selectforeground=TEXT,
            font=(FONT_FAMILY, 10),
            bd=0, highlightthickness=0,
            activestyle="none",
            selectmode="single",
        )
        self.listbox.pack(fill="both", expand=True, padx=1, pady=1)
        scrollbar.config(command=self.listbox.yview)

        # Drag-and-Drop innerhalb der Liste
        self.listbox.bind("<ButtonPress-1>",   self._on_drag_start)
        self.listbox.bind("<B1-Motion>",       self._on_drag_motion)
        self.listbox.bind("<ButtonRelease-1>", self._on_drag_release)
        self.listbox.bind("<Double-Button-1>", self._remove_selected)

        # Infozeile unter Liste
        self.info_label = tk.Label(
            left, text="Keine Dateien ausgewählt.",
            font=(FONT_FAMILY, 9), bg=BG, fg=TEXT_DIM, anchor="w",
        )
        self.info_label.pack(fill="x", pady=(4, 0))

        # Rechte Spalte: Schaltflächen
        right = tk.Frame(main, bg=BG, width=180)
        right.pack(side="right", fill="y", padx=(14, 0))
        right.pack_propagate(False)

        self._btn(right, "➕  Dateien hinzufügen", self._add_files, ACCENT, ACCENT_HOVER).pack(fill="x", pady=(0, 6))
        self._btn(right, "🗑  Ausgewählte entfernen", self._remove_selected, SURFACE2, BORDER).pack(fill="x", pady=(0, 6))
        self._btn(right, "✖  Alle entfernen", self._clear_all, SURFACE2, BORDER).pack(fill="x", pady=(0, 24))

        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=(0, 18))

        self._btn(right, "⬆  Nach oben", self._move_up,   SURFACE2, BORDER).pack(fill="x", pady=(0, 6))
        self._btn(right, "⬇  Nach unten", self._move_down, SURFACE2, BORDER).pack(fill="x", pady=(0, 24))

        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=(0, 18))

        # Merge-Button (prominent)
        self.merge_btn = self._btn(
            right, "🔀  PDFs zusammenführen",
            self._start_merge, SUCCESS, "#059669",
            font_size=11,
        )
        self.merge_btn.pack(fill="x")

        # ── Statusleiste ──────────────────────────────────────────────────────
        status_bar = tk.Frame(self, bg=SURFACE2, pady=8)
        status_bar.pack(fill="x", side="bottom")

        self.progress = ttk.Progressbar(
            status_bar, mode="indeterminate", length=160,
        )
        self.progress.pack(side="right", padx=14)

        self.status_var = tk.StringVar(value="Bereit.")
        tk.Label(
            status_bar, textvariable=self.status_var,
            font=(FONT_FAMILY, 9), bg=SURFACE2, fg=TEXT_DIM, anchor="w",
        ).pack(side="left", padx=14)

        # ttk-Stil für Progressbar
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "TProgressbar",
            troughcolor=SURFACE, background=ACCENT,
            darkcolor=ACCENT, lightcolor=ACCENT, bordercolor=SURFACE2,
        )

    # ── Hilfsmethode: Schaltfläche ─────────────────────────────────────────────
    def _btn(self, parent, text, cmd, color, hover_color, font_size=10):
        btn = tk.Label(
            parent, text=text,
            font=(FONT_FAMILY, font_size, "bold"),
            bg=color, fg=TEXT,
            pady=9, padx=10,
            cursor="hand2",
            anchor="w",
        )
        btn.bind("<Button-1>", lambda _: cmd())
        btn.bind("<Enter>",    lambda _: btn.configure(bg=hover_color))
        btn.bind("<Leave>",    lambda _: btn.configure(bg=color))
        return btn

    # ── Datei-Operationen ──────────────────────────────────────────────────────
    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="PDF-Dateien auswählen",
            filetypes=[("PDF-Dateien", "*.pdf"), ("Alle Dateien", "*.*")],
        )
        existing = list(self.listbox.get(0, "end"))
        added = 0
        for p in paths:
            if p not in existing:
                self.listbox.insert("end", p)
                added += 1
        self._refresh_info()
        if added:
            self._set_status(f"{added} Datei(en) hinzugefügt.")

    def _remove_selected(self, _event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        self.listbox.delete(sel[0])
        self._refresh_info()

    def _clear_all(self):
        if self.listbox.size() == 0:
            return
        if messagebox.askyesno("Alle entfernen", "Alle Dateien aus der Liste entfernen?"):
            self.listbox.delete(0, "end")
            self._refresh_info()
            self._set_status("Liste geleert.")

    def _move_up(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        i = sel[0]
        val = self.listbox.get(i)
        self.listbox.delete(i)
        self.listbox.insert(i - 1, val)
        self.listbox.select_set(i - 1)
        self.listbox.see(i - 1)

    def _move_down(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == self.listbox.size() - 1:
            return
        i = sel[0]
        val = self.listbox.get(i)
        self.listbox.delete(i)
        self.listbox.insert(i + 1, val)
        self.listbox.select_set(i + 1)
        self.listbox.see(i + 1)

    # ── Drag & Drop innerhalb der Liste ───────────────────────────────────────
    def _on_drag_start(self, event):
        self._drag_start = self.listbox.nearest(event.y)

    def _on_drag_motion(self, event):
        target = self.listbox.nearest(event.y)
        if self._drag_start is not None and target != self._drag_start:
            val = self.listbox.get(self._drag_start)
            self.listbox.delete(self._drag_start)
            self.listbox.insert(target, val)
            self.listbox.select_set(target)
            self._drag_start = target

    def _on_drag_release(self, _event):
        self._drag_start = None

    # ── Merge ──────────────────────────────────────────────────────────────────
    def _start_merge(self):
        files = list(self.listbox.get(0, "end"))
        if len(files) < 2:
            messagebox.showwarning(
                "Zu wenige Dateien",
                "Bitte mindestens 2 PDF-Dateien hinzufügen.",
            )
            return

        out_path = filedialog.asksaveasfilename(
            title="Ausgabedatei speichern",
            defaultextension=".pdf",
            filetypes=[("PDF-Dateien", "*.pdf")],
            initialfile="zusammengefuehrt.pdf",
        )
        if not out_path:
            return

        # Merge in eigenem Thread (UI bleibt reaktionsfähig)
        self.merge_btn.configure(bg="#6b7280", cursor="arrow")
        self.merge_btn.unbind("<Button-1>")
        self.progress.start(12)
        self._set_status(f"Zusammenführen von {len(files)} Dateien …")

        threading.Thread(
            target=self._merge_worker,
            args=(files, out_path),
            daemon=True,
        ).start()

    def _merge_worker(self, files: list[str], out_path: str):
        try:
            writer = PdfWriter()
            for path in files:
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)

            with open(out_path, "wb") as f:
                writer.write(f)

            self.after(0, self._merge_done, out_path, None)
        except Exception as exc:
            self.after(0, self._merge_done, out_path, str(exc))

    def _merge_done(self, out_path: str, error: str | None):
        self.progress.stop()
        # Merge-Button reaktivieren
        self.merge_btn.configure(bg=SUCCESS, cursor="hand2")
        self.merge_btn.bind("<Button-1>", lambda _: self._start_merge())

        if error:
            messagebox.showerror("Fehler beim Zusammenführen", error)
            self._set_status("Fehler aufgetreten.")
        else:
            filename = os.path.basename(out_path)
            self._set_status(f"✓ Gespeichert: {filename}")
            result = messagebox.askyesno(
                "Erfolgreich",
                f"Die Datei wurde erfolgreich erstellt:\n{out_path}\n\nDatei jetzt öffnen?",
            )
            if result:
                os.startfile(out_path)

    # ── Hilfsmethoden ─────────────────────────────────────────────────────────
    def _refresh_info(self):
        n = self.listbox.size()
        if n == 0:
            self.info_label.configure(text="Keine Dateien ausgewählt.")
        else:
            self.info_label.configure(text=f"{n} Datei(en) in der Liste · Reihenfolge per Drag & Drop oder ⬆⬇ anpassen")

    def _set_status(self, msg: str):
        self.status_var.set(msg)


if __name__ == "__main__":
    app = PDFMergerApp()
    app.mainloop()
