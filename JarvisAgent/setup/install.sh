#!/bin/bash
# Jarvis AI Agent - 一键安装脚本
# 支持 macOS 系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="Jarvis"
APP_PATH="/Applications/${APP_NAME}.app"
CONFIG_DIR="$HOME/.jarvis"
CONFIG_FILE="$CONFIG_DIR/config.json"

print_status() { echo -e "${GREEN}[OK]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[X]${NC} $1"; }
print_info() { echo -e "${BLUE}[i]${NC} $1"; }

print_banner() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}   Jarvis AI Agent - 智能桌面助手${NC}"
    echo -e "${BLUE}   版本 1.0.0 | 支持 GPT/豆包/MiniMax/千问${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

check_system() {
    print_info "检查系统..."
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "仅支持 macOS"
        exit 1
    fi
    print_status "系统检查完成"
}

check_dependencies() {
    print_info "检查依赖..."
    
    if ! command -v brew &> /dev/null; then
        print_warning "安装 Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装"
        exit 1
    fi
    
    print_status "依赖检查完成"
}

install_python_deps() {
    print_info "安装 Python 依赖..."
    
    cd "$PROJECT_DIR"
    
    python3 -m venv venv 2>/dev/null || true
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install pyautogui Pillow aiohttp beautifulsoup4 -q
    pip install pytesseract pynput -q
    deactivate
    
    print_status "Python 依赖安装完成"
}

install_system_deps() {
    print_info "安装系统依赖..."
    
    if ! command -v tesseract &> /dev/null; then
        print_warning "安装 tesseract..."
        brew install tesseract
        brew install tesseract-lang
    fi
    
    print_status "系统依赖安装完成"
}

build_app() {
    print_info "构建 Jarvis 应用..."
    
    cd "$PROJECT_DIR"
    python3 src/mac_app.py
    
    if [ -d "$APP_PATH" ]; then
        print_status "应用构建成功"
    else
        print_error "应用构建失败"
        exit 1
    fi
}

configure() {
    print_info "配置应用..."
    
    mkdir -p "$CONFIG_DIR"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        cp config/config.json "$CONFIG_FILE"
        chmod 600 "$CONFIG_FILE"
        print_status "配置已创建"
    fi
    
    print_info "请编辑 $CONFIG_FILE 添加 API 密钥"
}

setup_spotlight() {
    print_info "配置 Spotlight 集成..."
    python3 src/spotlight_launcher.py
    mdutil -E "$APP_PATH" 2>/dev/null || true
    print_status "Spotlight 集成完成"
}

setup_startup() {
    print_info "配置启动项..."
    
    PLIST_PATH="$HOME/Library/LaunchAgents/com.jarvis.agent.plist"
    
    cat > "$PLIST_PATH" << EOF
<?xml version="1.0"?>
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jarvis.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/venv/bin/python</string>
        <string>$PROJECT_DIR/src/agent_core.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF
    
    print_status "启动项配置完成"
}

verify() {
    print_info "验证安装..."
    
    ERRORS=0
    
    [ -d "$APP_PATH" ] || { print_error "应用未找到"; ERRORS=$((ERRORS + 1)); }
    [ -f "$CONFIG_FILE" ] || { print_error "配置未找到"; ERRORS=$((ERRORS + 1)); }
    [ -d "$PROJECT_DIR/venv" ] || { print_error "虚拟环境未找到"; ERRORS=$((ERRORS + 1)); }
    
    if [ $ERRORS -eq 0 ]; then
        print_status "安装验证通过"
    fi
}

show_instructions() {
    echo ""
    echo -e "${GREEN}安装完成！${NC}"
    echo ""
    echo -e "${YELLOW}使用方法:${NC}"
    echo ""
    echo "  1. Spotlight 搜索: 按 Cmd+Space，输入 'Jarvis'"
    echo "  2. 全局热键: Ctrl+Cmd+J 呼出 Jarvis"
    echo "  3. 启动台: 在 Launchpad 中找到 Jarvis"
    echo ""
    echo -e "${YELLOW}配置 AI 服务:${NC}"
    echo ""
    echo "  编辑配置文件: open ~/.jarvis/config.json"
    echo "  启用所需的 AI 服务并添加 API 密钥"
    echo ""
    echo -e "${YELLOW}常用命令:${NC}"
    echo ""
    echo "  查看日志: tail -f /tmp/jarvis_agent.log"
    echo "  停止服务: launchctl unload ~/Library/LaunchAgents/com.jarvis.agent.plist"
    echo ""
}

main() {
    print_banner
    check_system
    check_dependencies
    install_python_deps
    install_system_deps
    build_app
    configure
    setup_spotlight
    setup_startup
    verify
    show_instructions
}

main "$@"
