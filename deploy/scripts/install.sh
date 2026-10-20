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

# Configuration
INSTALL_DIR="/opt/hound"
HOUND_USER="hound"

echo "Installing dependencies..."
apt-get update
apt-get install -y \
    docker.io \
    docker-compose-plugin \
    curl \
    git \
    firefox-esr \
    x11-utils \
    xserver-xorg \
    x11-xserver-utils || true

# Install docker-compose standalone if plugin not available
if ! command -v docker &> /dev/null; then
    echo "Docker not found, installing..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Check for docker-compose
if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "Installing docker-compose standalone..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo "Creating Hound user..."
if ! id "$HOUND_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d "$INSTALL_DIR" "$HOUND_USER"
fi

echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
chown "$HOUND_USER:$HOUND_USER" "$INSTALL_DIR"

echo "Copying Hound files..."
# This assumes the script is run from the Hound repository
cp -r . "$INSTALL_DIR/"
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
