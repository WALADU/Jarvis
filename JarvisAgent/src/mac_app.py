#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Jarvis AI Agent - macOS应用包装器
 版本: 1.0.0
 功能: 创建macOS应用包，实现从启动台和Spotlight启动
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import subprocess


class MacOSAppBuilder:
    """macOS应用构建器"""
    
    def __init__(self, app_name: str = "Jarvis", app_path: str = None):
        """
        初始化应用构建器
        
        Args:
            app_name: 应用名称
            app_path: 应用输出路径
        """
        self.app_name = app_name
        self.app_path = app_path or f"/Applications/{app_name}.app"
        self.source_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def build(self) -> bool:
        """
        构建macOS应用包
        
        Returns:
            是否成功
        """
        try:
            print(f"开始构建 {self.app_name}.app...")
            
            # 创建目录结构
            self._create_directory_structure()
            
            # 创建Info.plist
            self._create_info_plist()
            
            # 创建主程序脚本
            self._create_main_script()
            
            # 创建启动画面
            self._create_launch_screen()
            
            # 复制资源文件
            self._copy_resources()
            
            # 设置权限
            self._set_permissions()
            
            # 注册应用
            self._register_app()
            
            print(f"应用构建成功: {self.app_path}")
            return True
            
        except Exception as e:
            print(f"应用构建失败: {e}")
            return False
    
    def _create_directory_structure(self):
        """创建目录结构"""
        paths = [
            f"{self.app_path}/Contents",
            f"{self.app_path}/Contents/MacOS",
            f"{self.app_path}/Contents/Resources",
            f"{self.app_path}/Contents/Resources/App.icns"
        ]
        
        for path in paths:
            Path(path).mkdir(parents=True, exist_ok=True)
    
    def _create_info_plist(self):
        """创建Info.plist"""
        plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>zh_CN</string>
    <key>CFBundleDisplayName</key>
    <string>Jarvis</string>
    <key>CFBundleExecutable</key>
    <string>Jarvis</string>
    <key>CFBundleIconFile</key>
    <string>App.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.jarvis.agent</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Jarvis</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright 2024. All rights reserved.</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>NSUIElement</key>
    <false/>
    <key>CFBundleURLTypes</key>
    <array>
        <dict>
            <key>CFBundleURLName</key>
            <string>com.jarvis.agent</string>
            <key>CFBundleURLSchemes</key>
            <array>
                <string>jarvis</string>
            </array>
        </dict>
    </array>
    <key>LSMultipleInstancesProhibited</key>
    <false/>
    <key>LSBackgroundOnly</key>
    <false/>
</dict>
</plist>'''
        
        info_plist_path = f"{self.app_path}/Contents/Info.plist"
        with open(info_plist_path, 'w', encoding='utf-8') as f:
            f.write(plist_content)
        
        print(f"Info.plist已创建: {info_plist_path}")
    
    def _create_main_script(self):
        """创建主程序脚本"""
        main_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Jarvis AI Agent - macOS主入口
"""

import sys
import os

# 添加源目录到路径
source_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, source_path)

# 导入并启动Agent
from agent_core import JarvisAgent

def main():
    """主函数"""
    print("启动 Jarvis AI Agent...")
    
    # 加载配置
    config_path = os.path.expanduser("~/.jarvis/config.json")
    
    # 启动Agent
    agent = JarvisAgent(config_path)
    
    try:
        # 保持运行
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()
        print("Jarvis 已停止")

if __name__ == "__main__":
    main()
'''
        
        main_script_path = f"{self.app_path}/Contents/MacOS/Jarvis"
        with open(main_script_path, 'w', encoding='utf-8') as f:
            f.write(main_script)
        
        print(f"主程序已创建: {main_script_path}")
    
    def _create_launch_screen(self):
        """创建启动画面"""
        # 创建简单的HTML启动画面
        html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Jarvis AI Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            overflow: hidden;
        }
        .logo {
            font-size: 80px;
            font-weight: bold;
            color: #4A90D9;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }
        .title {
            font-size: 32px;
            margin-bottom: 10px;
        }
        .subtitle {
            font-size: 16px;
            color: #888;
        }
        .loading {
            margin-top: 30px;
            display: flex;
            gap: 8px;
        }
        .loading span {
            width: 12px;
            height: 12px;
            background: #4A90D9;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .loading span:nth-child(1) { animation-delay: -0.32s; }
        .loading span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
    </style>
</head>
<body>
    <div class="logo">J</div>
    <div class="title">Jarvis AI Agent</div>
    <div class="subtitle">正在启动...</div>
    <div class="loading">
        <span></span>
        <span></span>
        <span></span>
    </div>
</body>
</html>
'''
        
        launch_screen_path = f"{self.app_path}/Contents/Resources/launch_screen.html"
        with open(launch_screen_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"启动画面已创建: {launch_screen_path}")
    
    def _copy_resources(self):
        """复制资源文件"""
        source_resources = Path(self.source_path) / "resources"
        target_resources = f"{self.app_path}/Contents/Resources"
        
        if source_resources.exists():
            # 复制所有资源
            for item in source_resources.iterdir():
                target = target_resources / item.name
                if item.is_dir():
                    shutil.copytree(item, target)
                else:
                    shutil.copy2(item, target)
        
        # 创建默认配置文件
        self._create_default_config()
        
        print(f"资源已复制到: {target_resources}")
    
    def _create_default_config(self):
        """创建默认配置文件"""
        config = {
            "ai_services": {
                "openai": {"enabled": False, "api_key": "", "model": "gpt-4"},
                "doubao": {"enabled": False, "api_key": "", "model": "doubao-pro-32k"},
                "minimax": {"enabled": False, "api_key": "", "model": "abab6.5s-chat"},
                "qwen": {"enabled": False, "api_key": "", "model": "qwen-turbo"}
            },
            "automation": {
                "screenshot_path": "/tmp/jarvis_screenshots",
                "download_path": "~/Downloads",
                "paper_storage": "~/Desktop/Papers"
            },
            "general": {
                "language": "zh",
                "theme": "dark",
                "startup": True,
                "hotkey": "<ctrl>+<cmd>+j"
            },
            "integrations": {
                "spotlight": True,
                "alfred": False,
                "quicksilver": False
            }
        }
        
        config_path = Path(os.path.expanduser("~/.jarvis/config.json"))
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"默认配置已创建: {config_path}")
    
    def _set_permissions(self):
        """设置权限"""
        executable_path = f"{self.app_path}/Contents/MacOS/Jarvis"
        if os.path.exists(executable_path):
            os.chmod(executable_path, 0o755)
            print(f"权限已设置: {executable_path}")
    
    def _register_app(self):
        """注册应用"""
        try:
            # 使用系统命令刷新
            subprocess.run(
                ['/usr/bin/python3', '-m', 'plistutil', 
                 f"{self.app_path}/Contents/Info.plist"],
                capture_output=True
            )
            
            print(f"应用已注册: {self.app_path}")
            
        except Exception as e:
            print(f"应用注册时出现警告: {e}")
    
    def create_icon(self):
        """创建应用图标"""
        # 创建.icns图标文件
        # 使用sips和iconutil创建图标
        try:
            # 创建临时图片
            temp_icon_path = "/tmp/jarvis_icon.png"
            icon_size = (1024, 1024)
            
            # 使用Python创建简单图标
            from PIL import Image, ImageDraw
            
            img = Image.new('RGBA', icon_size, (74, 144, 217, 255))
            draw = ImageDraw.Draw(img)
            
            # 绘制圆角矩形
            draw.rounded_rectangle(
                [(0, 0), icon_size], 
                radius=200, 
                fill=(74, 144, 217)
            )
            
            # 绘制字母J
            from PIL import ImageFont
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 500)
            except:
                font = ImageFont.load_default()
            
            draw.text(
                (512, 512), 
                "J", 
                fill="white", 
                anchor="mm",
                font=font
            )
            
            img.save(temp_icon_path)
            
            # 转换为.icns格式
            icon_path = f"{self.app_path}/Contents/Resources/App.icns"
            subprocess.run(
                ['sips', '-s', 'format', 'icns', temp_icon_path, 
                 '--out', icon_path],
                capture_output=True
            )
            
            # 清理临时文件
            os.remove(temp_icon_path)
            
            print(f"图标已创建: {icon_path}")
            
        except Exception as e:
            print(f"创建图标时出现警告: {e}")
    
    def uninstall(self):
        """卸载应用"""
        try:
            if os.path.exists(self.app_path):
                shutil.rmtree(self.app_path)
                print(f"应用已卸载: {self.app_path}")
                return True
        except Exception as e:
            print(f"卸载失败: {e}")
            return False


class JarvisMenuBarApp:
    """Jarvis菜单栏应用"""
    
    def __init__(self):
        self.app_path = "/Applications/Jarvis.app"
        self.source_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def create_menu_bar_app(self) -> bool:
        """
        创建菜单栏应用
        
        Returns:
            是否成功
        """
        try:
            # 创建菜单栏应用脚本
            menubar_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Jarvis AI Agent - 菜单栏应用
"""

import os
import sys
from PyObjCTools import AppHelper
from Foundation import NSObject, NSMenu, NSMenuItem
from AppKit import NSApplication, NSStatusBar, NSVariableStatusItemLength

class JarvisMenuBarApp(NSApplication):
    """Jarvis菜单栏应用"""
    
    def finishLaunching(self):
        """启动完成"""
        super().finishLaunching()
        
        # 创建状态栏项目
        self.statusBar = NSStatusBar.systemStatusBar()
        self.statusItem = self.statusBar.statusItemWithLength_(
            NSVariableStatusItemLength
        )
        
        # 设置菜单
        self._setup_menu()
        
        # 设置图标
        self._setup_icon()
        
        print("Jarvis 菜单栏应用已启动")
    
    def _setup_menu(self):
        """设置菜单"""
        # 创建菜单
        self.menu = NSMenu.new()
        
        # 添加菜单项
        items = [
            ("显示 Jarvis", self._show_window),
            ("执行命令...", self._show_command_dialog),
            ("-", None),
            ("帮助", self._show_help),
            ("退出", self._quit)
        ]
        
        for title, action in items:
            if title == "-":
                self.menu.addItem_(NSMenuItem.separatorItem())
            else:
                item = NSMenuItem.new()
                item.setTitle_(title)
                if action:
                    self.setTarget_forAction_(action, item)
                self.menu.addItem_(item)
        
        self.statusItem.setMenu_(self.menu)
    
    def _setup_icon(self):
        """设置图标"""
        try:
            from PyObjCTools.AppHelper import installMenu
            pass
        except:
            pass
    
    def _show_window(self):
        """显示窗口"""
        print("显示 Jarvis 窗口")
    
    def _show_command_dialog(self):
        """显示命令对话框"""
        print("显示命令对话框")
    
    def _show_help(self):
        """显示帮助"""
        print("显示帮助")
    
    def _quit(self):
        """退出"""
        NSApplication.sharedApplication().terminate_(None)


def main():
    """主函数"""
    app = JarvisMenuBarApp.sharedApplication()
    app.finishLaunching()
    AppHelper.runEventLoop()


if __name__ == "__main__":
    main()
'''
            
            menubar_path = f"{self.app_path}/Contents/Resources/menubar_app.py"
            with open(menubar_path, 'w', encoding='utf-8') as f:
                f.write(menubar_script)
            
            print(f"菜单栏应用已创建: {menubar_path}")
            return True
            
        except Exception as e:
            print(f"创建菜单栏应用失败: {e}")
            return False


def build_jarvis_app() -> bool:
    """
    构建完整的Jarvis应用
    
    Returns:
        是否成功
    """
    builder = MacOSAppBuilder("Jarvis")
    
    # 构建主应用
    success = builder.build()
    
    if success:
        # 创建图标
        builder.create_icon()
        
        # 创建菜单栏应用
        menu_app = JarvisMenuBarApp()
        menu_app.create_menu_bar_app()
    
    return success


def uninstall_jarvis_app() -> bool:
    """
    卸载Jarvis应用
    
    Returns:
        是否成功
    """
    builder = MacOSAppBuilder("Jarvis")
    return builder.uninstall()


if __name__ == "__main__":
    # 构建应用
    build_jarvis_app()
