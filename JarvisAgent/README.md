# Jarvis AI Agent

## 您的智能桌面助手

一个强大的 macOS 桌面 AI 助手，支持从 Spotlight 呼出。

### 功能特性

- 多模型支持：GPT-4、豆包、MiniMax、千问
- 电脑操作自动化：应用控制、文件管理、网页操作
- Spotlight 深度集成：支持 /jarvis 呼出
- 全局热键：Ctrl+Cmd+J 快速启动
- 智能任务规划和执行

### 系统要求

- macOS 11.0 或更高版本
- Python 3.8+
- Homebrew

### 快速安装

```bash
# 克隆项目
git clone https://github.com/yourusername/jarvis-agent.git
cd jarvis-agent

# 运行安装脚本
chmod +x setup/install.sh
./setup/install.sh
```

### 配置 AI 服务

编辑 `~/.jarvis/config.json`：

```json
{
    "ai_services": {
        "openai": {
            "enabled": true,
            "api_key": "your-api-key"
        }
    }
}
```

### 使用方法

1. **Spotlight 呼出**：按 Cmd+Space，输入 "jarvis"
2. **全局热键**：Ctrl+Cmd+J
3. **启动台**：在 Launchpad 中找到 Jarvis

### 卸载

```bash
rm -rf /Applications/Jarvis.app
rm -rf ~/.jarvis
rm ~/Library/LaunchAgents/com.jarvis.agent.plist
```

### 详细文档

查看 [安装教程](SETUP_GUIDE.md) 了解更多详情。

---

MIT License
