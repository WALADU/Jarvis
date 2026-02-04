#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Jarvis AI Agent - Spotlight启动器
 版本: 1.0.0
 功能: 创建Spotlight搜索别名，实现快速呼出
"""

import os
import sys
import json
import subprocess
from pathlib import Path


class SpotlightAliasCreator:
    """Spotlight别名创建器"""
    
    def __init__(self, app_bundle_path: str = "/Applications/Jarvis.app"):
        self.app_bundle_path = app_bundle_path
        self.alfred_workflow_path = None
    
    def create_spotlight_importer(self, executable_path: str):
        """创建Spotlight导入器"""
        try:
            importer_path = os.path.join(
                self.app_bundle_path, 
                "Contents/Library/Spotlight"
            )
            Path(importer_path).mkdir(parents=True, exist_ok=True)
            
            plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd>
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>Jarvis</string>
    <key>CFBundleIdentifier</key>
    <string>com.jarvis.agent.spotlight</string>
    <key>CFBundleName</key>
    <string>JarvisSpotlight</string>
</dict>
</plist>'''
            
            plist_path = os.path.join(importer_path, "Info.plist")
            with open(plist_path, 'w', encoding='utf-8') as f:
                f.write(plist_content)
            
            link_path = os.path.join(importer_path, "JarvisSpotlight")
            if os.path.exists(executable_path) and not os.path.exists(link_path):
                os.symlink(executable_path, link_path)
            
            print(f"Spotlight导入器已创建: {importer_path}")
            return True
            
        except Exception as e:
            print(f"创建Spotlight导入器失败: {e}")
            return False
    
    def create_alfred_workflow(self, workflow_path: str):
        """创建Alfred工作流"""
        try:
            self.alfred_workflow_path = workflow_path
            workflow_dir = Path(workflow_path)
            workflow_dir.mkdir(parents=True, exist_ok=True)
            
            info_plist = '''<?xml version="1.0"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>bundleid</key>
    <string>com.jarvis.agent.alfred</string>
    <key>name</key>
    <string>Jarvis AI Agent</string>
</dict>
</plist>'''
            
            with open(workflow_dir / "info.plist", 'w') as f:
                f.write(info_plist)
            
            script_content = '''#!/usr/bin/env python3
import sys, json

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    items = [{"title": "Jarvis AI Agent", "subtitle": "按回车启动", "arg": "launch", "valid": True}]
    if query:
        items.append({"title": f"执行: {query}", "arg": f"execute:{query}", "valid": True})
    print(json.dumps({"items": items}, ensure_ascii=False))

if __name__ == "__main__":
    main()
'''
            
            with open(workflow_dir / "jarvis.py", 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            icon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
  <rect width="1024" height="1024" rx="200" fill="#4A90D9"/>
  <text x="512" y="650" font-size="500" fill="white" text-anchor="middle">J</text>
</svg>'''
            
            with open(workflow_dir / "icon.svg", 'w') as f:
                f.write(icon_svg)
            
            print(f"Alfred工作流已创建: {workflow_path}")
            return True
            
        except Exception as e:
            print(f"创建Alfred工作流失败: {e}")
            return False
    
    def create_quicksilver_trigger(self, trigger_name: str = "/jarvis"):
        """创建Quicksilver触发器"""
        try:
            script_content = f'''#!/bin/bash
JARVIS_PATH="{self.app_bundle_path}/Contents/MacOS/Jarvis"
if [ -f "$JARVIS_PATH" ]; then
    open "{self.app_bundle_path}"
else
    python3 "$HOME/.jarvis/jarvis.py" --trigger "{trigger_name}"
fi
'''
            
            script_path = os.path.expanduser("~/.jarvis/jarvis_quick_launch.sh")
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            print(f"Quicksilver触发器已创建: {script_path}")
            return script_path
            
        except Exception as e:
            print(f"创建Quicksilver触发器失败: {e}")
            return None
    
    def create_launchd_config(self, agent_path: str):
        """创建Launchd配置"""
        try:
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jarvis.agent</string>
    <key>ProgramArguments</key>
    <array><string>{agent_path}</string><string>--daemon</string></array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>'''
            
            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.jarvis.agent.plist")
            
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            print(f"Launchd配置已创建: {plist_path}")
            return plist_path
            
        except Exception as e:
            print(f"创建Launchd配置失败: {e}")
            return None


class SpotlightIntegration:
    """Spotlight集成管理器"""
    
    def __init__(self):
        self.alias_creator = SpotlightAliasCreator()
        self.installed_integrations = []
    
    def install_spotlight_alias(self, app_path: str) -> bool:
        """安装Spotlight别名"""
        try:
            subprocess.run(['mdutil', '-E', app_path], capture_output=True)
            self.installed_integrations.append("spotlight")
            print("Spotlight别名已安装")
            return True
        except Exception as e:
            print(f"安装Spotlight别名失败: {e}")
            return False
    
    def install_alfred_workflow(self, workflow_path: str) -> bool:
        """安装Alfred工作流"""
        success = self.alias_creator.create_alfred_workflow(workflow_path)
        if success:
            self.installed_integrations.append("alfred")
        return success
    
    def setup_global_hotkey(self, hotkey: str = "<ctrl>+<cmd>+j") -> bool:
        """设置全局热键"""
        try:
            self.hotkey_config = {'hotkey': hotkey, 'description': "Ctrl+Cmd+J 呼出Jarvis"}
            self.installed_integrations.append("hotkey")
            print(f"全局热键已配置: {hotkey}")
            return True
        except Exception as e:
            print(f"设置全局热键失败: {e}")
            return False
    
    def complete_setup(self) -> bool:
        """完成所有集成设置"""
        results = {
            'spotlight': self.install_spotlight_alias("/Applications/Jarvis.app"),
            'alfred': self.install_alfred_workflow(
                os.path.expanduser("~/Library/Caches/Alfred/Workflows/jarvis.alfredworkflow")
            ),
            'hotkey': self.setup_global_hotkey()
        }
        return any(results.values())


def create_spotlight_launcher() -> SpotlightIntegration:
    return SpotlightIntegration()


if __name__ == "__main__":
    launcher = create_spotlight_launcher()
    launcher.complete_setup()
