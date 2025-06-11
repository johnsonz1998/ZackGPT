#!/bin/bash

echo "🧨 Stopping Colima..."
colima stop

echo "🧹 Cleaning Docker cache and metadata..."
docker builder prune -a --force
docker system prune -a --volumes --force

echo "💽 Restarting Colima with fresh settings..."
colima start --cpu 4 --memory 6 --disk 100

echo "🔧 Rebuilding Docker image..."
docker compose build --no-cache

echo "🚀 Launching ZackGPT..."
docker compose up
