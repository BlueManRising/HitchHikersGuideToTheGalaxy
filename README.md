# 🌌 Hitchhiker's Guide to the Galaxy — Raspberry Pi Edition

> “Don’t Panic.” – The Guide

A fullscreen interactive touchscreen app styled after the *Hitchhiker's Guide to the Galaxy*, built for Raspberry Pi. Combines beautiful UI, animated buttons, quirky Guide content, and live AI interaction powered by TinyLlama via [Ollama](https://ollama.com).

![be3e1a32-46bf-445f-8c3d-0f5cc499b1eb~1](https://github.com/user-attachments/assets/80b0b532-f293-4fbb-b3c0-fa898c19e65b)


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
    - I used a 7" LCD Dsplay C 1024x600 USB Touch screen
- Raspberry Pi OS (Desktop is prefered since it has all the GUI loaded)
    - I used a Pi 5 with 16gb of Ram   
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
    - I dont have a Keyboard setup, so if you want to integrate a small factor keyboard, do it!
- Swipe or tap arrow buttons to scroll
- Quit with the `QUIT` button or `Ctrl+C` from terminal
- All content (meaning the button menus) is editable via the `assets/pages/` folder, it just pulls a txt file, meant to be fun.

---

## 🛠 Developer Notes

- Me and GPT got it done, I wanted this so bad, 
- Built with `pygame`
- All animations, layout, and logic in `main.py`
- Fonts and images stored in `assets/`

---
## AI notes:

I specifically made the AI talk as if its the guide, now as cool as it is, its a little wordy... (i even did try to make it shorter, but its ignoring me in true Douglass Adas fashon)

Find the following section in the code (around line 107) and change it if you want :)

# --- BUILD PROMPT FUNCTION ---
def build_prompt(user_query):
    system_prompt = (
        "You are the Hitchhiker's Guide to the Galaxy. "
        "Respond in a quirky, dry, and witty style as if written by Douglas Adams. "
        "Keep your answers extremely short—only one or two sentences."
    )
    return system_prompt + "\n" + user_query

---

## ☕ Contribute

Fork, star, or submit a PR! If you’ve got ideas for new categories or features, feel free to open an issue.

---

## 📡 License

MIT — remix, adapt, or take this Guide with you wherever you go (even Betelgeuse).

---

**Don’t Panic. Just touch the screen.**
