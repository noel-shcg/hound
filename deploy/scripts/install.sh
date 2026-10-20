#!/bin/bash
# Hound Installation Script
# This script installs Hound on a Linux system

set -e

echo "Hound Installation Script"
echo "========================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Get the script directory and find repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "Repository directory: $REPO_DIR"

# Configuration
INSTALL_DIR="/opt/hound"
HOUND_USER="hound"

echo "Updating package lists..."
apt-get update

echo "Installing dependencies..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git || true

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sh /tmp/get-docker.sh
    rm /tmp/get-docker.sh
    usermod -aG docker "$HOUND_USER" || true
fi

# Install docker-compose if not available via plugin
if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "Installing docker-compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Install other dependencies
apt-get install -y \
    firefox-esr \
    x11-utils \
    xserver-xorg \
    x11-xserver-utils || true

echo "Creating Hound user..."
if ! id "$HOUND_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d "$INSTALL_DIR" "$HOUND_USER"
    usermod -aG docker "$HOUND_USER" || true
fi

echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
chown "$HOUND_USER:$HOUND_USER" "$INSTALL_DIR"

echo "Copying Hound files from $REPO_DIR to $INSTALL_DIR..."
cp -r "$REPO_DIR"/* "$INSTALL_DIR/"
chown -R "$HOUND_USER:$HOUND_USER" "$INSTALL_DIR"

echo "Setting up environment file..."
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    chown "$HOUND_USER:$HOUND_USER" "$INSTALL_DIR/.env"
    echo "Environment file created. Please edit $INSTALL_DIR/.env with your configuration."
fi

echo "Installing systemd services..."
cp "$INSTALL_DIR/deploy/systemd/hound.service" /etc/systemd/system/
cp "$INSTALL_DIR/deploy/systemd/hound-kiosk.service" /etc/systemd/system/
cp "$INSTALL_DIR/deploy/systemd/hound-auto-update.service" /etc/systemd/system/
cp "$INSTALL_DIR/deploy/systemd/hound-auto-update.timer" /etc/systemd/system/
chmod +x /etc/systemd/system/hound*.service /etc/systemd/system/hound*.timer
chmod +x "$INSTALL_DIR/deploy/scripts/auto-update.sh"
chmod +x "$INSTALL_DIR/deploy/kiosk/hound-kiosk.sh"
systemctl daemon-reload

echo "Enabling Hound service..."
systemctl enable hound.service

echo "Enabling auto-update timer..."
systemctl enable hound-auto-update.timer

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit $INSTALL_DIR/.env with your configuration"
echo "2. Generate a secure secret key and update HOUND_SECRET_KEY"
echo "3. Start Hound: systemctl start hound"
echo "4. Enable kiosk mode (optional): systemctl enable --now hound-kiosk"
echo ""
echo "Auto-update is enabled by default (runs daily)"
echo "To disable: systemctl disable hound-auto-update.timer"
echo "To check update status: journalctl -u hound-auto-update"
echo ""
echo "The dashboard will be available at http://localhost:3000"
echo "The management interface will be available at http://localhost:3000/management"
