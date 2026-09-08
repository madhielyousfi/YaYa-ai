#!/bin/bash

# ============================================
#  YOYO SHORTS - Smart Launcher
#  Runs Backend + Frontend with nice TUI
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Project paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
VENV_DIR="$SCRIPT_DIR/.venv"
API_PORT=8000
FRONTEND_PORT=3000

# ============================================
#  Pretty UI Functions
# ============================================

print_header() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║   ██╗   ██╗ ██████╗  ██████╗ █████╗ ██╗                    ║"
    echo "║   ██║   ██║██╔═══██╗██╔════╝██╔══██╗██║                    ║"
    echo "║   ██║   ██║██║   ██║██║     ███████║██║                    ║"
    echo "║   ╚██╗ ██╔╝██║   ██║██║     ██╔══██║██║                    ║"
    echo "║    ╚████╔╝ ╚██████╔╝╚██████╗██║  ██║███████╗               ║"
    echo "║     ╚═══╝   ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝               ║"
    echo "║                                                            ║"
    echo "║          🎬 AI Video Generator - Smart Launcher            ║"
    echo "║                                                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}  [$1/6]${NC} ${WHITE}$2${NC}"
}

print_success() {
    echo -e "  ${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "  ${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "  ${RED}✗${NC} $1"
}

print_info() {
    echo -e "  ${GRAY}ℹ${NC} $1"
}

print_loading() {
    echo -ne "  ${CYAN}⟳${NC} $1"
}

spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    while [ "$(ps -p $pid -o pid= 2>/dev/null)" ]; do
        for (( i=0; i<${#spinstr}; i++ )); do
            echo -ne "\r  ${CYAN}${spinstr:$i:1}${NC} $2"
            sleep $delay
        done
    done
    echo -ne "\r"
}

# ============================================
#  Dependency Management
# ============================================

check_command() {
    command -v "$1" &>/dev/null
}

install_python_deps() {
    print_step "1" "Checking Python environment..."
    
    if ! check_command python3; then
        print_error "Python3 not found!"
        echo -e "  ${YELLOW}Install with:${NC} sudo apt install python3 python3-pip python3-venv"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1)
    print_success "Python found: $python_version"
    
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_success "Virtual environment exists"
    fi
    
    source "$VENV_DIR/bin/activate"
    
    print_info "Installing Python packages..."
    pip install -q --upgrade pip
    pip install -q -r "$BACKEND_DIR/pyproject.toml" 2>/dev/null || true
    pip install -q typer pydantic pydantic-settings httpx edge-tts pillow python-dotenv fastapi uvicorn websockets 2>/dev/null
    
    print_success "Python packages installed"
}

install_node_deps() {
    print_step "2" "Checking Node.js environment..."
    
    if ! check_command node; then
        print_error "Node.js not found!"
        echo -e "  ${YELLOW}Install with:${NC}"
        echo -e "    ${GRAY}curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -${NC}"
        echo -e "    ${GRAY}sudo apt install -y nodejs${NC}"
        exit 1
    fi
    
    node_version=$(node --version)
    npm_version=$(npm --version)
    print_success "Node.js found: $node_version (npm: $npm_version)"
    
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        print_info "Installing frontend packages..."
        cd "$FRONTEND_DIR"
        npm install --silent 2>/dev/null
        print_success "Frontend packages installed"
    else
        print_success "Frontend packages exist"
    fi
}

check_ollama() {
    print_step "3" "Checking Ollama (AI engine)..."
    
    if check_command ollama; then
        if curl -s http://localhost:11434/api/tags &>/dev/null; then
            print_success "Ollama is running"
            
            models=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; print([m['name'] for m in json.load(sys.stdin).get('models',[])])" 2>/dev/null || echo "[]")
            if [ "$models" = "[]" ]; then
                print_warning "No models installed"
                echo -e "  ${YELLOW}Install a model with:${NC} ollama pull qwen2.5:3b"
            else
                print_success "Models: $models"
            fi
        else
            print_warning "Ollama installed but not running"
            echo -e "  ${YELLOW}Start with:${NC} ollama serve"
        fi
    else
        print_warning "Ollama not installed (optional)"
        echo -e "  ${GRAY}Install: https://ollama.com${NC}"
    fi
}

check_ffmpeg() {
    print_step "4" "Checking FFmpeg (video engine)..."
    
    if check_command ffmpeg; then
        ffmpeg_version=$(ffmpeg -version 2>&1 | head -1 | cut -d' ' -f3)
        print_success "FFmpeg found: v$ffmpeg_version"
    else
        print_error "FFmpeg not found!"
        echo -e "  ${YELLOW}Install with:${NC} sudo apt install ffmpeg"
        exit 1
    fi
}

check_api_keys() {
    print_step "5" "Checking API keys..."
    
    if [ -f "$BACKEND_DIR/.env" ]; then
        source "$BACKEND_DIR/.env"
        
        if [ -n "$PEXELS_API_KEY" ] && [ "$PEXELS_API_KEY" != "" ]; then
            print_success "Pexels API key configured"
        else
            print_warning "Pexels API key missing"
            echo -e "  ${GRAY}Get free key: https://www.pexels.com/api/${NC}"
        fi
        
        if [ -n "$PIXABAY_API_KEY" ] && [ "$PIXABAY_API_KEY" != "" ]; then
            print_success "Pixabay API key configured"
        else
            print_warning "Pixabay API key missing"
            echo -e "  ${GRAY}Get free key: https://pixabay.com/api/docs/${NC}"
        fi
    else
        print_warning ".env file not found"
        echo -e "  ${YELLOW}Copy .env.example to .env and add your API keys${NC}"
    fi
}

# ============================================
#  Server Management
# ============================================

start_backend() {
    print_step "6" "Starting backend server..."
    
    cd "$BACKEND_DIR"
    source "$VENV_DIR/bin/activate"
    
    uvicorn api.main:app --host 0.0.0.0 --port $API_PORT &>/tmp/yoyo_api.log &
    API_PID=$!
    
    sleep 2
    
    if kill -0 $API_PID 2>/dev/null; then
        if curl -s http://localhost:$API_PORT/health &>/dev/null; then
            print_success "Backend running on port $API_PORT"
        else
            print_warning "Backend started but health check failed"
        fi
    else
        print_error "Backend failed to start"
        echo -e "  ${GRAY}Check logs: /tmp/yoyo_api.log${NC}"
    fi
}

start_frontend() {
    print_info "Starting frontend server..."
    
    cd "$FRONTEND_DIR"
    npm run dev &>/tmp/yoyo_frontend.log &
    FRONTEND_PID=$!
    
    sleep 3
    
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        print_success "Frontend running on port $FRONTEND_PORT"
    else
        print_warning "Frontend may still be starting..."
    fi
}

# ============================================
#  Cleanup
# ============================================

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    
    if [ ! -z "$API_PID" ] && kill -0 $API_PID 2>/dev/null; then
        kill $API_PID 2>/dev/null
        print_info "Backend stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID 2>/dev/null
        print_info "Frontend stopped"
    fi
    
    echo -e "${GREEN}Goodbye! 👋${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# ============================================
#  Main
# ============================================

main() {
    print_header
    
    echo -e "${MAGENTA}  Starting Yoyo Shorts...${NC}"
    echo ""
    
    install_python_deps
    install_node_deps
    check_ollama
    check_ffmpeg
    check_api_keys
    
    echo ""
    echo -e "${CYAN}  ─────────────────────────────────────────────────────────${NC}"
    echo ""
    
    start_backend
    start_frontend
    
    echo ""
    echo -e "${CYAN}  ════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${GREEN}${BOLD}🚀 Yoyo Shorts is ready!${NC}"
    echo ""
    echo -e "  ${WHITE}Open in your browser:${NC}"
    echo -e "  ${CYAN}${BOLD}  http://localhost:$FRONTEND_PORT${NC}"
    echo ""
    echo -e "  ${WHITE}API docs:${NC}"
    echo -e "  ${GRAY}  http://localhost:$API_PORT/docs${NC}"
    echo ""
    echo -e "${CYAN}  ════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${GRAY}Press Ctrl+C to stop all servers${NC}"
    echo ""
    
    # Open browser automatically (optional)
    if check_command xdg-open; then
        xdg-open "http://localhost:$FRONTEND_PORT" 2>/dev/null &
    elif check_command open; then
        open "http://localhost:$FRONTEND_PORT" 2>/dev/null &
    fi
    
    # Keep script running
    wait
}

# Run
main
