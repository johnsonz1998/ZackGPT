#!/bin/bash

# ZackGPT UI Launcher
# This script starts the Angular development server for ZackGPT's web interface

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}=====================================
🤖 ZackGPT Web UI Launcher
=====================================${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js first.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Please install npm first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js version: $(node --version)${NC}"
echo -e "${GREEN}✅ npm version: $(npm --version)${NC}"

# Navigate to UI directory
if [ ! -d "ui/zackgpt-ui" ]; then
    echo -e "${RED}❌ UI directory not found. Make sure you're in the ZackGPT root directory.${NC}"
    exit 1
fi

cd ui/zackgpt-ui

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    npm install
fi

# Check if backend is running
echo -e "${YELLOW}🔍 Checking if ZackGPT backend is running...${NC}"
if curl -s http://localhost:8000/api/stats > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running and accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Backend doesn't seem to be running on port 8000${NC}"
    echo -e "${YELLOW}   You may need to start the ZackGPT backend first${NC}"
    echo -e "${YELLOW}   Run: ./zackgpt.sh${NC}"
fi

# Start the development server
echo -e "${BLUE}🚀 Starting Angular development server...${NC}"
echo -e "${GREEN}📱 UI will be available at: http://localhost:4200${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
echo ""

# Start with production-like settings for better performance
npm run start -- --open --host 0.0.0.0 