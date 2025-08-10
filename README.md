# Flip Clock (PySide6)

A clean, frameless, **transparent flip clock** for Windows/macOS/Linux built with **PySide6 (Qt)**.  
Pin it on top, resize it, and keep your desktop classy.

> Minimal, distraction‑free, and open source.

---

## ✨ Features
- Split‑flap **flip animation** for `HH:MM:SS`
- **Transparent** background & **frameless** window (no title bar or system buttons)
- **Always‑on‑top** toggle via **right‑click** menu (Pin/Unpin)
- **Resizable**:
  - Right‑click → **Size** → Small / Medium / Large / XL / XXL
  - **Shortcuts:** `Ctrl + =` to increase, `Ctrl + -` to decrease, `Ctrl + 0` to reset
  - Drag the **bottom‑right corner** to scale
- **Centered on launch**, drag anywhere to move
- No drop shadow on the cards (clean, flat look)

---

## 📦 Project Structure
```
.
├── src/
│   └── flip_clock.py               # App source (PySide6)
├── packaging/
│   ├── build_onedir.bat            # Folder app (fast startup)
│   └── build_onefile.bat           # Single EXE (easy to share)
├── .github/workflows/build.yml     # CI: builds Windows exe on tagged release
├── requirements.txt                # PySide6
├── LICENSE                         # MIT
└── README.md                       # This file
```

---

## 🚀 Quick Start (Dev)
1) **Install Python 3.10+** (3.12 recommended).  
2) Install dependencies:
```bash
pip install -r requirements.txt
```
3) Run:
```bash
python src/flip_clock.py
```
> Windows tip: use `pythonw.exe src/flip_clock.py` to hide the console window.

---

## 🖱️ Usage
- **Move:** Left‑click and drag anywhere on the clock
- **Context menu:** Right‑click anywhere
  - **Pin / Unpin** (always‑on‑top)
  - **Size** presets
  - **Exit**
- **Keyboard shortcuts:**
  - `Ctrl + =` Increase size
  - `Ctrl + -` Decrease size
  - `Ctrl + 0` Reset size

---

## 🧰 Build a Desktop App (PyInstaller)

### Windows (recommended)
**One‑folder app (faster startup):**
```bash
pyinstaller --windowed --noconsole --name FlipClock --collect-all PySide6 src/flip_clock.py
```
Result: `dist/FlipClock/FlipClock.exe`

**Single‑file EXE (easy to share):**
```bash
pyinstaller --onefile --windowed --noconsole --name FlipClock --collect-all PySide6 src/flip_clock.py
```
Result: `dist/FlipClock.exe`

> If you prefer, use the helper scripts in `/packaging` by double‑clicking them.

### macOS (Intel/Apple Silicon)
```bash
python -m pip install pyinstaller
pyinstaller --windowed --noconsole --name FlipClock --collect-all PySide6 src/flip_clock.py
```
Run the app from `dist/FlipClock.app`.  
> For sharing outside your machine you’ll likely need to **codesign** and optionally **notarize**.

### Linux
```bash
python -m pip install pyinstaller
pyinstaller --windowed --name FlipClock --collect-all PySide6 src/flip_clock.py
```
Run from `dist/FlipClock/`.

---

## 🔁 Run at Startup (Windows)
1. Build your EXE (see above).  
2. Press `Win + R`, type `shell:startup`, press Enter.  
3. Put a **shortcut** to your `FlipClock.exe` in that folder.  
   - To avoid a console window, build with `--windowed`/`--noconsole` or run via `pythonw.exe`.

---

## 🛠️ CI: GitHub Actions
When you push a tag like `v1.0.0`, the workflow in `.github/workflows/build.yml` will:
- Build a Windows EXE with PyInstaller
- Upload it as a Release asset

Create a release tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 🧯 Troubleshooting
- **No EXE after build:** You’re probably looking at the `build/` folder. The app is in **`dist/`**.  
- **Antivirus quarantined the EXE:** Add an exception or sign the binary.  
- **Blurry UI on high‑DPI displays (Windows):** try adding before `QApplication`:
  ```python
  from PySide6.QtGui import QGuiApplication
  QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
      Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
  )
  ```
- **Import errors:** Ensure `PySide6` is installed in the same Python environment used by PyInstaller.

---

## 🤝 Contributing
PRs are welcome!  
Ideas/TODOs:
- Save & restore **size/position/pin** state
- 12/24h toggle & themes
- Optional **seconds** hide / minimal mode
- Multi‑monitor placement memory

1. Fork → create a branch → commit changes → open a PR.  
2. Keep code formatted and documented.

---

## 📄 License
MIT © {author}
