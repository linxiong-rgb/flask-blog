#!/bin/bash
# Render build script - 安装中文字体

echo "========================================="
echo "Installing Chinese fonts..."
echo "========================================="

# 更新包管理器并安装中文字体
apt-get update -qq
apt-get install -y fonts-wqy-zenhei fonts-wqy-microhei fonts-noto-cjk

echo "Chinese fonts installed:"
fc-list :lang=zh | head -3

echo "========================================="
echo "Installing Python dependencies..."
echo "========================================="
pip install -r requirements.txt

echo "Build completed!"
