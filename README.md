# 🌌 Hitchhiker's Guide to the Galaxy — Raspberry Pi Edition

> “Don’t Panic.” – The Guide

A fullscreen interactive touchscreen app styled after the *Hitchhiker's Guide to the Galaxy*, built for Raspberry Pi. Combines beautiful UI, animated buttons, quirky Guide content, and live AI interaction powered by TinyLlama via [Ollama](https://ollama.com).

---

## 📸 Features

- Fullscreen, mouse-free touch interface
- Douglas Adams-style answers from a local LLM
- Animated button transitions + popup content
- Built-in categories like: `WHO`, `WHAT`, `WHY`, `WHERE`, `WHEN`, `HOW`
- Offline-ready: All content and AI run locally
- Auto-start on boot (optional)

---

## ⚙️ Requirements

- Raspberry Pi (any model with a touchscreen)
- Raspberry Pi OS (Lite or Desktop)
- Python 3.7+
- [Ollama](https://ollama.com) with `tinyllama` pulled
- Internet connection (for initial install only)

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/hitchhikers-guide-pi.git
cd hitchhikers-guide-pi
```

### 2. Run the Installer
This script sets up everything: dependencies, Ollama, and optionally enables auto-start.

```bash
chmod +x install.sh
./install.sh
```

You’ll be asked:
> 🔁 Would you like to auto-start the Guide on boot? (y/n)

If you say yes:
- Ollama runs on boot
- The Guide launches automatically in fullscreen

---

## 🧠 Local AI Powered by TinyLlama

This app uses [Ollama](https://ollama.com) to run the `tinyllama` model locally:
```bash
ollama run tinyllama
```

> Note: The first run will download the model (~500MB).

No API keys. No internet required once installed.

---

## 💡 Tips

- Tap `THE GUIDE` for LLM interaction
- Swipe or tap arrow buttons to scroll
- Quit with the `QUIT` button or `Ctrl+C` from terminal
- All content is editable via the `assets/pages/` folder

---

## 🛠 Developer Notes

- Built with `pygame`
- All animations, layout, and logic in `main.py`
- Fonts and images stored in `assets/`

---

## ☕ Contribute

Fork, star, or submit a PR! If you’ve got ideas for new categories or features, feel free to open an issue.

---

## 📡 License

MIT — remix, adapt, or take this Guide with you wherever you go (even Betelgeuse).

---

**Don’t Panic. Just touch the screen.**
