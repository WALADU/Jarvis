# Jarvis AI Agent - Mac 安装指南

## 目录
1. 系统要求
2. 快速安装
3. 配置 AI 服务
4. 使用方法
5. 故障排除
6. 卸载

## 1. 系统要求
- macOS 11.0+
- Python 3.8+
- Homebrew
- 2GB 可用磁盘空间

## 2. 快速安装

### 步骤 1：克隆项目
```bash
cd ~/Documents
git clone https://github.com/yourusername/jarvis-agent.git
cd jarvis-agent
```

### 步骤 2：创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

### 步骤 3：安装依赖
```bash
pip install --upgrade pip
pip install pyautogui Pillow aiohttp beautifulsoup4
pip install pytesseract pynput
brew install tesseract
```

### 步骤 4：构建应用
```bash
python3 src/mac_app.py
```

### 步骤 5：配置 Spotlight
```bash
python3 src/spotlight_launcher.py
mdutil -E /Applications/Jarvis.app
```

### 步骤 6：设置权限
1. 系统设置 > 隐私与安全性 > 辅助功能 > 添加 Jarvis
2. 系统设置 > 隐私与安全性 > 屏幕录制 > 添加 Jarvis

## 3. 配置 AI 服务

编辑 ~/.jarvis/config.json：

```json
{
    "ai_services": {
        "openai": {
            "enabled": true,
            "api_key": "your-api-key",
            "model": "gpt-4"
        },
        "doubao": {
            "enabled": true,
            "api_key": "your-api-key"
        }
    }
}
```

## 4. 使用方法

### 呼出 Jarvis
- Spotlight: 按 Cmd+Space，输入 "jarvis"
- 全局热键: Ctrl+Cmd+J

### 常用命令
```
"帮我搜索 AI 最新论文"
"打开 Safari 浏览器"
"下载这个文件: https://xxx.com/file.pdf"
"整理下载文件夹"
```

## 5. 故障排除

### Spotlight 搜索不到
```bash
mdutil -E /Applications/Jarvis.app
killall SystemUIServer
```

### 权限问题
- 系统设置 > 隐私与安全性 > 辅助功能 > 添加 Jarvis

### API 调用失败
- 检查 API Key 是否正确
- 查看日志: tail -f /tmp/jarvis_agent.log

## 6. 卸载
```bash
rm -rf /Applications/Jarvis.app
rm -rf ~/.jarvis
rm ~/Library/LaunchAgents/com.jarvis.agent.plist
```

## 详细文档
查看 README.md 获取完整文档。
