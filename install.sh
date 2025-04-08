#!/bin/bash

echo "🌌 Setting up the Hitchhiker's Guide on your Raspberry Pi..."

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system dependencies
sudo apt install -y python3 python3-pip python3-dev \
  libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
  curl git

# Install Python dependencies
pip3 install pygame

# Install Ollama if not already installed
if ! command -v ollama &> /dev/null; then
  echo "🚀 Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "✅ Ollama already installed."
fi

# Pull the TinyLlama model (will prompt if not running Ollama yet)
echo "📦 Pulling TinyLlama model (this may take a few minutes)..."
ollama pull tinyllama

# Prompt for autostart option
read -p "🔁 Would you like to auto-start the Guide on boot? (y/n): " autostart
if [[ "$autostart" == "y" || "$autostart" == "Y" ]]; then
  SERVICE_DIR="/etc/systemd/system"
  USER_NAME=$(whoami)
  WORK_DIR=$(pwd)
  PY_EXEC=$(which python3)

  echo "📝 Creating systemd services..."

  # 1. Ollama service
  sudo bash -c "cat > $SERVICE_DIR/ollama.service" <<EOL
[Unit]
Description=Ollama LLM Server
After=network.target

[Service]
ExecStart=/usr/local/bin/ollama serve
Restart=always
User=${USER_NAME}
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

  # 2. Hitchhiker's Guide service (depends on Ollama)
  sudo bash -c "cat > $SERVICE_DIR/hitchhikers_guide.service" <<EOL
[Unit]
Description=Hitchhiker's Guide Touchscreen App
After=ollama.service
Requires=ollama.service

[Service]
ExecStart=${PY_EXEC} ${WORK_DIR}/main.py
WorkingDirectory=${WORK_DIR}
StandardOutput=inherit
StandardError=inherit
Restart=always
User=${USER_NAME}
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

  echo "🔄 Enabling and starting services..."
  sudo systemctl daemon-reexec
  sudo systemctl daemon-reload
  sudo systemctl enable ollama
  sudo systemctl enable hitchhikers_guide
  sudo systemctl start ollama
  sleep 2
  sudo systemctl start hitchhikers_guide

  echo "✅ Auto-start is enabled! The Guide and Ollama will launch on boot."
else
  echo "🕹️ Skipping autostart setup. You can always add it later!"
fi

echo "🎬 You can now run the app manually with:"
echo "    python3 main.py"
