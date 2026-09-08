#!/bin/bash

# ============================================
#  YOYO SHORTS - Stop Script
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════╗"
echo "║     Stopping Yoyo Shorts Servers         ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# Kill backend
echo -ne "  Stopping backend..."
if pkill -f "uvicorn api.main" 2>/dev/null; then
    echo -e " ${GREEN}✓${NC}"
else
    echo -e " ${YELLOW}(not running)${NC}"
fi

# Kill frontend
echo -ne "  Stopping frontend..."
if pkill -f "next dev" 2>/dev/null; then
    echo -e " ${GREEN}✓${NC}"
else
    echo -e " ${YELLOW}(not running)${NC}"
fi

# Kill any remaining processes on ports
echo -ne "  Cleaning up port 8000..."
fuser -k 8000/tcp 2>/dev/null && echo -e " ${GREEN}✓${NC}" || echo -e " ${YELLOW}(clear)${NC}"

echo -ne "  Cleaning up port 3000..."
fuser -k 3000/tcp 2>/dev/null && echo -e " ${GREEN}✓${NC}" || echo -e " ${YELLOW}(clear)${NC}"

echo ""
echo -e "  ${GREEN}All servers stopped! 👋${NC}"
echo ""
