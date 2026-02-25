#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Preparing host dependencies for Docker + NVIDIA runtime..."

# Keep package metadata fresh before toolkit installation.
sudo apt-get update

# Allow current user to run docker without sudo after next login/session.
if getent group docker >/dev/null 2>&1; then
  sudo usermod -aG docker "${USER}"
fi

if ! dpkg -s nvidia-container-toolkit >/dev/null 2>&1; then
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
    | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed "s#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g" \
    | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list >/dev/null
  sudo apt-get update
  sudo apt-get install -y nvidia-container-toolkit
else
  echo "[INFO] nvidia-container-toolkit already installed, skip install."
fi

sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

echo "[INFO] Preparation completed."
echo "[INFO] If docker permission still fails, log out and log in again to refresh docker group."
