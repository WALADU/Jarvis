#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Jarvis AI Agent - 计算机视觉模块
 版本: 1.0.0
 功能: 提供屏幕截图、UI元素识别和目标检测能力
"""

import os
import sys
import time
import logging
import threading
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import base64
from io import BytesIO

try:
    import pyautogui
    import pyscreeze
    from PIL import Image, ImageDraw, ImageFont
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    logger.warning("截图功能不可用，请安装依赖: pip install pyautogui Pillow")

try:
    from pyobjc import Quarz, Cocoa
    import Quartz
    import AppKit
    MACOS_CV_AVAILABLE = True
except ImportError:
    MACOS_CV_AVAILABLE = False

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """屏幕截图管理器"""
    
    def __init__(self, save_dir: str = "/tmp/jarvis_screenshots"):
        """
        初始化截图管理器
        
        Args:
            save_dir: 截图保存目录
        """
        self.save_dir = save_dir
        self._ensure_directory()
        
        self.capturing = False
        self.capture_thread = None
    
    def _ensure_directory(self):
        """确保目录存在"""
        Path(self.save_dir).mkdir(parents=True, exist_ok=True)
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        截取屏幕截图
        
        Args:
            filename: 文件名（可选）
            
        Returns:
            截图文件路径
        """
        if not SCREENSHOT_AVAILABLE:
            raise Exception("截图功能不可用")
        
        try:
            # 生成文件名
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(self.save_dir, filename)
            
            # 使用pyautogui截图
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            logger.info(f"截图已保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            raise
    
    def take_region_screenshot(
        self, 
        left: int, 
        top: int, 
        width: int, 
        height: int,
        filename: str = None
    ) -> str:
        """
        截取屏幕区域
        
        Args:
            left: 左上角X坐标
            top: 左上角Y坐标
            width: 宽度
            height: 高度
            filename: 文件名
            
        Returns:
            截图文件路径
        """
        if not SCREENSHOT_AVAILABLE:
            raise Exception("截图功能不可用")
        
        try:
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_region_{timestamp}.png"
            
            filepath = os.path.join(self.save_dir, filename)
            
            # 截取指定区域
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot.save(filepath)
            
            logger.info(f"区域截图已保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"区域截图失败: {e}")
            raise
    
    def start_continuous_capture(self, interval: float = 1.0):
        """
        开始连续截图
        
        Args:
            interval: 截图间隔（秒）
        """
        if self.capturing:
            return
        
        self.capturing = True
        self.capture_thread = threading.Thread(
            target=self._continuous_capture_loop,
            args=(interval,),
            daemon=True
        )
        self.capture_thread.start()
    
    def stop_continuous_capture(self):
        """停止连续截图"""
        self.capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
    
    def _continuous_capture_loop(self, interval: float):
        """连续截图循环"""
        while self.capturing:
            try:
                self.take_screenshot()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"连续截图错误: {e}")
                time.sleep(1)
    
    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        if SCREENSHOT_AVAILABLE:
            return pyautogui.size()
        return (0, 0)
    
    def get_screen_resolution(self) -> Dict:
        """获取屏幕分辨率信息"""
        if SCREENSHOT_AVAILABLE:
            size = pyautogui.size()
            return {
                "width": size.width,
                "height": size.height,
                "primary": True
            }
        return {}


class UIElementDetector:
    """UI元素检测器"""
    
    def __init__(self):
        """初始化UI元素检测器"""
        self.screenshot_manager = ScreenshotManager()
        
        # UI元素特征库
        self.element_patterns = {
            'button': ['按钮', 'button', '点击', '确认', '取消', 'submit', 'ok', 'cancel'],
            'input': ['输入', 'input', '搜索', 'search', '文本框', 'textfield'],
            'link': ['链接', 'link', '超链接', 'hyperlink'],
            'menu': ['菜单', 'menu', '导航', 'navigation'],
            'checkbox': ['复选框', 'checkbox', '勾选', '选择'],
            'radio': ['单选', 'radio', '选项'],
            'scrollbar': ['滚动', 'scroll', '滑块', 'slider'],
            'window': ['窗口', 'window', '对话框', 'dialog']
        }
    
    def detect_elements(
        self, 
        image_path: str = None,
        screenshot = None
    ) -> List[Dict]:
        """
        检测屏幕上的UI元素
        
        Args:
            image_path: 图片路径
            screenshot: PIL图片对象
            
        Returns:
            检测到的UI元素列表
        """
        elements = []
        
        try:
            # 获取截图
            if image_path:
                img = Image.open(image_path)
            elif screenshot:
                img = screenshot
            else:
                img = self.screenshot_manager.take_screenshot()
            
            # 使用AI分析图像
            elements = self._analyze_image_with_ai(img)
            
        except Exception as e:
            logger.error(f"UI元素检测失败: {e}")
        
        return elements
    
    def _analyze_image_with_ai(self, img) -> List[Dict]:
        """
        使用AI分析图像识别UI元素
        
        Args:
            img: PIL图片对象
            
        Returns:
            UI元素列表
        """
        # 将图像转为base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # 这里是简化版本，实际应该调用AI服务分析
        # 返回空列表表示需要进一步处理
        return []
    
    def find_element_by_text(
        self, 
        text: str, 
        image_path: str = None
    ) -> Optional[Dict]:
        """
        根据文本查找UI元素
        
        Args:
            text: 元素文本
            image_path: 图片路径
            
        Returns:
            找到的元素信息
        """
        try:
            # 使用pyautogui查找元素
            location = pyautogui.locateOnScreen(
                self._create_text_image(text),
                confidence=0.8
            )
            
            if location:
                return {
                    'text': text,
                    'position': {
                        'left': location.left,
                        'top': location.top,
                        'width': location.width,
                        'height': location.height
                    },
                    'center': {
                        'x': location.left + location.width // 2,
                        'y': location.top + location.height // 2
                    }
                }
                
        except Exception as e:
            logger.error(f"查找元素失败: {e}")
        
        return None
    
    def _create_text_image(self, text: str) -> str:
        """创建文本图像用于匹配"""
        # 实际实现需要创建临时图像
        return None
    
    def find_click_target(self, instruction: str) -> Tuple[int, int]:
        """
        根据指令查找点击目标
        
        Args:
            instruction: 操作指令
            
        Returns:
            点击坐标 (x, y)
        """
        try:
            # 尝试直接匹配
            for keyword, patterns in self.element_patterns.items():
                if any(pattern in instruction.lower() for pattern in patterns):
                    # 查找对应类型的元素
                    element = self._find_element_by_type(keyword)
                    if element:
                        return element['center']['x'], element['center']['y']
            
            # 如果找不到，使用AI分析
            screenshot = self.screenshot_manager.take_screenshot()
            target = self._analyze_click_target(instruction, screenshot)
            
            if target:
                return target
            
        except Exception as e:
            logger.error(f"查找点击目标失败: {e}")
        
        # 默认返回屏幕中心
        size = self.screenshot_manager.get_screen_size()
        return size.width // 2, size.height // 2
    
    def _find_element_by_type(self, element_type: str) -> Optional[Dict]:
        """根据类型查找元素"""
        # 简化实现
        return None
    
    def _analyze_click_target(
        self, 
        instruction: str, 
        screenshot_path: str
    ) -> Optional[Tuple[int, int]]:
        """
        使用AI分析点击目标
        
        Args:
            instruction: 操作指令
            screenshot_path: 截图路径
            
        Returns:
            点击坐标
        """
        # 实际实现应该调用AI服务
        return None


class TextRecognizer:
    """文本识别器"""
    
    def __init__(self):
        """初始化文本识别器"""
        self.screenshot_manager = ScreenshotManager()
    
    def recognize_text(
        self, 
        image_path: str = None,
        region: Tuple = None
    ) -> str:
        """
        识别图像中的文字
        
        Args:
            image_path: 图片路径
            region: 识别区域 (left, top, width, height)
            
        Returns:
            识别的文本
        """
        try:
            if image_path:
                img = Image.open(image_path)
            else:
                img = self.screenshot_manager.take_screenshot()
            
            if region:
                img = img.crop(region)
            
            # 使用pytesseract识别文字
            # 需要安装tesseract: brew install tesseract
            import pytesseract
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"文字识别失败: {e}")
            return ""
    
    def recognize_text_from_screen(
        self, 
        left: int, 
        top: int, 
        width: int, 
        height: int
    ) -> str:
        """
        识别屏幕指定区域的文字
        
        Args:
            left: 左上角X坐标
            top: 左上角Y坐标
            width: 宽度
            height: 高度
            
        Returns:
            识别的文本
        """
        return self.recognize_text(region=(left, top, width, height))
    
    def extract_structured_data(self, image_path: str) -> Dict:
        """
        从图像中提取结构化数据
        
        Args:
            image_path: 图片路径
            
        Returns:
            结构化数据
        """
        text = self.recognize_text(image_path)
        
        # 解析文本为结构化数据
        data = {
            'raw_text': text,
            'lines': text.split('\n'),
            'words': text.split()
        }
        
        return data


class ComputerVision:
    """
    计算机视觉主类
    整合所有视觉相关功能
    """
    
    def __init__(self):
        """初始化计算机视觉系统"""
        self.screenshot_manager = ScreenshotManager()
        self.element_detector = UIElementDetector()
        self.text_recognizer = TextRecognizer()
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        截取屏幕截图
        
        Args:
            filename: 文件名
            
        Returns:
            截图文件路径
        """
        return self.screenshot_manager.take_screenshot(filename)
    
    def take_region_screenshot(
        self, 
        left: int, 
        top: int, 
        width: int, 
        height: int,
        filename: str = None
    ) -> str:
        """
        截取屏幕区域
        
        Args:
            left: 左上角X坐标
            top: 左上角Y坐标
            width: 宽度
            height: 高度
            filename: 文件名
            
        Returns:
            截图文件路径
        """
        return self.screenshot_manager.take_region_screenshot(
            left, top, width, height, filename
        )
    
    def find_click_target(self, instruction: str) -> Tuple[int, int]:
        """
        根据指令查找点击位置
        
        Args:
            instruction: 操作指令
            
        Returns:
            点击坐标 (x, y)
        """
        return self.element_detector.find_click_target(instruction)
    
    def recognize_screen_text(self, region: Tuple = None) -> str:
        """
        识别屏幕文字
        
        Args:
            region: 识别区域
            
        Returns:
            识别的文本
        """
        if region:
            left, top, width, height = region
            return self.text_recognizer.recognize_text_from_screen(
                left, top, width, height
            )
        else:
            return self.text_recognizer.recognize_text()
    
    def detect_ui_elements(self) -> List[Dict]:
        """
        检测屏幕上的UI元素
        
        Returns:
            UI元素列表
        """
        return self.element_detector.detect_elements()
    
    def get_screen_info(self) -> Dict:
        """获取屏幕信息"""
        return {
            'size': self.screenshot_manager.get_screen_size(),
            'resolution': self.screenshot_manager.get_screen_resolution()
        }
    
    def start_monitoring(self, interval: float = 5.0):
        """
        开始屏幕监控
        
        Args:
            interval: 检查间隔（秒）
        """
        def monitor_loop():
            while True:
                try:
                    # 定期截取屏幕
                    self.screenshot_manager.take_screenshot()
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"屏幕监控错误: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        
        logger.info("屏幕监控已启动")
    
    def compare_screenshots(
        self, 
        image_path1: str, 
        image_path2: str
    ) -> Dict:
        """
        比较两张截图的差异
        
        Args:
            image_path1: 第一张图片路径
            image_path2: 第二张图片路径
            
        Returns:
            差异信息
        """
        try:
            img1 = Image.open(image_path1)
            img2 = Image.open(image_path2)
            
            # 计算差异
            diff = ImageChrors.difference(img1, img2)
            
            # 检查是否有显著差异
            pixels_different = sum(1 for pixel in diff.getdata() if pixel != 0)
            total_pixels = diff.size[0] * diff.size[1]
            diff_ratio = pixels_different / total_pixels
            
            return {
                'has_difference': diff_ratio > 0.01,
                'difference_ratio': diff_ratio,
                'pixels_different': pixels_different
            }
            
        except Exception as e:
            logger.error(f"截图比较失败: {e}")
            return {'has_difference': False}
    
    def highlight_element(self, element: Dict, duration: float = 1.0):
        """
        高亮显示指定元素
        
        Args:
            element: 元素信息
            duration: 高亮持续时间
        """
        position = element.get('position', {})
        left = position.get('left', 0)
        top = position.get('top', 0)
        width = position.get('width', 100)
        height = position.get('height', 50)
        
        # 创建高亮图像
        screenshot = pyautogui.screenshot()
        draw = ImageDraw.Draw(screenshot)
        
        # 绘制高亮框
        draw.rectangle(
            [left, top, left + width, top + height],
            outline='red',
            width=3
        )
        
        # 保存临时高亮图像
        highlight_path = '/tmp/jarvis_highlight.png'
        screenshot.save(highlight_path)
        
        # 显示一段时间
        time.sleep(duration)
        
        # 恢复原始截图
        os.remove(highlight_path)


def install_dependencies():
    """安装计算机视觉依赖"""
    import subprocess
    
    dependencies = [
        'pyautogui',
        'pyscreeze',
        'Pillow',
        'pytesseract'
    ]
    
    for dep in dependencies:
        try:
            subprocess.run(
                ['pip', 'install', dep],
                check=True
            )
            logger.info(f"已安装: {dep}")
        except subprocess.CalledProcessError:
            logger.error(f"安装失败: {dep}")
    
    # 安装tesseract
    try:
        subprocess.run(
            ['brew', 'install', 'tesseract'],
            check=True
        )
        logger.info("已安装: tesseract")
    except subprocess.CalledProcessError:
        logger.warning("tesseract安装失败，请手动安装")
