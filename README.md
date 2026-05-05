# PDF Merger

Lokale Windows-Anwendung zum Zusammenführen mehrerer PDF-Dateien in einer  
benutzerdefinierten Reihenfolge.

---

## Schnellstart (fertige EXE)

Wenn du die fertige `PDF_Merger.exe` erhalten hast:

1. Die Datei 'PDF_Merger.exe' liegt im Verzeichnis 'dist'. Das ist die einzige Datei, die ihr wirklich benötigt.
2. Datei irgendwo ablegen (z. B. Desktop)
3. Doppelklick → fertig, **keine Installation nötig**

---

## Selbst bauen (Entwickler)

### Voraussetzungen

| Was | Version |
|-----|---------|
| Python | 3.10 oder höher |
| pip | aktuell |

Python herunterladen: https://www.python.org/downloads/  
Bei der Installation **„Add Python to PATH"** aktivieren.

### Schritt 1 – Abhängigkeiten & EXE erzeugen

```bat
build.bat
```

Das Skript installiert `pypdf` und `PyInstaller` und erstellt anschließend  
`dist\PDF_Merger.exe`.

### Schritt 2 – Direkt starten (ohne EXE)

```bat
pip install pypdf
python pdf_merger.py
```

---

## Bedienung

| Aktion | Beschreibung |
|--------|--------------|
| **➕ Dateien hinzufügen** | Mehrere PDFs auf einmal auswählen |
| **Drag & Drop** | Einträge in der Liste per Maus verschieben |
| **⬆ / ⬇** | Ausgewählten Eintrag einen Schritt verschieben |
| **Doppelklick** | Datei aus der Liste entfernen |
| **🔀 PDFs zusammenführen** | Ausgabedatei auswählen und zusammenführen |

---

## Verwendete Bibliotheken (Open Source)

| Bibliothek | Lizenz | Zweck |
|------------|--------|-------|
| [pypdf](https://github.com/py-pdf/pypdf) | BSD-3-Clause | PDF lesen & schreiben |
| [PyInstaller](https://pyinstaller.org) | GPL-2.0 + Bootloader-Ausnahme | Standalone-EXE erzeugen |
| tkinter | PSF (Teil von Python) | Benutzeroberfläche |

---

## Verteilung an Kollegen

Nur die Datei `dist\PDF_Merger.exe` weitergeben – fertig.  
Kein Python, kein pip, keine Installation erforderlich.

> **Hinweis:** Einige Virenscanner melden PyInstaller-EXEs fälschlicherweise  
> als verdächtig (False Positive). Die Datei ist sicher; ggf. eine Ausnahme  
> in Windows Defender hinzufügen.
