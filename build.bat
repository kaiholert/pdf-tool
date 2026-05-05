@echo off
REM ============================================================
REM  PDF Merger – Build-Skript  (einmalig ausführen)
REM  Erzeugt:  dist\PDF_Merger.exe  (standalone, kein Python nötig)
REM ============================================================

echo.
echo [1/3] Abhangigkeiten installieren...
pip install pypdf pyinstaller --quiet
if errorlevel 1 (
    echo FEHLER: pip install fehlgeschlagen.
    pause
    exit /b 1
)

echo.
echo [2/3] Anwendung kompilieren...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "PDF_Merger" ^
    --clean ^
    pdf_merger.py

if errorlevel 1 (
    echo FEHLER: PyInstaller fehlgeschlagen.
    pause
    exit /b 1
)

echo.
echo [3/3] Fertig!
echo.
echo  Die fertige EXE-Datei liegt unter:
echo     dist\PDF_Merger.exe
echo.
echo  Diese Datei kann direkt an Kollegen weitergegeben werden.
echo  Es ist keine Python-Installation erforderlich.
echo.
pause
