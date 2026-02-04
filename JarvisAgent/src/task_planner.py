#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Jarvis AI Agent - 任务规划器
 版本: 1.0.0
 功能: 智能任务分解、调度和执行管理
"""

import os
import sys
import json
import time
import logging
import threading
import uuid
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import queue

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """任务优先级枚举"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"


@dataclass
class Task:
    """任务数据类"""
    id: str
    type: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    
    # 任务详情
    instruction: str = ""
    params: Dict = field(default_factory=dict)
    
    # 依赖关系
    dependencies: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    
    # 执行信息
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # 结果
    result: Any = None
    error: Optional[str] = None
    
    # 元数据
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'type': self.type,
            'description': self.description,
            'priority': self.priority.value,
            'status': self.status.value,
            'instruction': self.instruction,
            'params': self.params,
            'dependencies': self.dependencies,
            'subtasks': self.subtasks,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'result': self.result,
            'error': self.error,
            'tags': self.tags,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """从字典创建任务"""
        priority = TaskPriority(data.get('priority', 3))
        status = TaskStatus(data.get('status', 'pending'))
        
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            type=data.get('type', 'general'),
            description=data.get('description', ''),
            priority=priority,
            status=status,
            instruction=data.get('instruction', ''),
            params=data.get('params', {}),
            dependencies=data.get('dependencies', []),
            subtasks=data.get('subtasks', []),
            created_at=data.get('created_at', datetime.now().isoformat()),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at'),
            result=data.get('result'),
            error=data.get('error'),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {})
        )


class TaskPlanner:
    """
    任务规划器
    负责任务的创建、分解、调度和执行管理
    """
    
    def __init__(self, persistence_path: str = None):
        """
        初始化任务规划器
        
        Args:
            persistence_path: 任务持久化路径
        """
        self.persistence_path = persistence_path or "/tmp/jarvis_tasks"
        Path(self.persistence_path).mkdir(parents=True, exist_ok=True)
        
        # 任务存储
        self.tasks: Dict[str, Task] = {}
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        
        # 任务依赖图
        self.dependency_graph: Dict[str, List[str]] = {}
        
        # 执行器
        self.executors: Dict[str, Callable] = {}
        self.execution_threads: Dict[str, threading.Thread] = {}
        
        # 状态
        self.is_running = False
        self.current_task_id = None
        
        # 锁
        self.lock = threading.Lock()
        
        # 事件
        self.task_completed_event = threading.Event()
        
        # 加载已保存的任务
        self._load_tasks()
    
    def register_executor(self, task_type: str, executor: Callable):
        """
        注册任务执行器
        
        Args:
            task_type: 任务类型
            executor: 执行函数
        """
        self.executors[task_type] = executor
        logger.info(f"已注册任务执行器: {task_type}")
    
    def create_task(
        self,
        task_type: str,
        description: str,
        instruction: str = "",
        params: Dict = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: List[str] = None,
        tags: List[str] = None,
        **kwargs
    ) -> str:
        """
        创建新任务
        
        Args:
            task_type: 任务类型
            description: 任务描述
            instruction: 任务指令
            params: 任务参数
            priority: 优先级
            dependencies: 依赖的任务ID列表
            tags: 任务标签
            
        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())[:8]
        
        task = Task(
            id=task_id,
            type=task_type,
            description=description,
            instruction=instruction,
            params=params or {},
            priority=priority,
            dependencies=dependencies or [],
            tags=tags or []
        )
        
        # 更新依赖图
        self.dependency_graph[task_id] = task.dependencies
        for dep_id in task.dependencies:
            if dep_id in self.dependency_graph:
                self.dependency_graph[dep_id].append(task_id)
        
        # 保存任务
        self.tasks[task_id] = task
        self._save_task(task)
        
        logger.info(f"任务已创建: {task_id} - {description}")
        
        return task_id
    
    def create_subtask(
        self,
        parent_task_id: str,
        task_type: str,
        description: str,
        instruction: str = "",
        params: Dict = None,
        **kwargs
    ) -> str:
        """
        创建子任务
        
        Args:
            parent_task_id: 父任务ID
            task_type: 任务类型
            description: 任务描述
            instruction: 任务指令
            params: 任务参数
            
        Returns:
            子任务ID
        """
        subtask_id = self.create_task(
            task_type=task_type,
            description=description,
            instruction=instruction,
            params=params,
            **kwargs
        )
        
        # 添加到父任务的子任务列表
        if parent_task_id in self.tasks:
            self.tasks[parent_task_id].subtasks.append(subtask_id)
        
        return subtask_id
    
    def decompose_task(
        self,
        task_id: str,
        decomposition_strategy: str = "auto"
    ) -> List[str]:
        """
        分解任务为子任务
        
        Args:
            task_id: 任务ID
            decomposition_strategy: 分解策略
            
        Returns:
            子任务ID列表
        """
        if task_id not in self.tasks:
            logger.error(f"任务不存在: {task_id}")
            return []
        
        task = self.tasks[task_id]
        
        # 根据任务类型进行分解
        if task.type == 'search_download':
            return self._decompose_search_download(task)
        elif task.type == 'file_organize':
            return self._decompose_file_organize(task)
        elif task.type == 'web_operation':
            return self._decompose_web_operation(task)
        elif task.type == 'complex_analysis':
            return self._decompose_complex_analysis(task)
        else:
            # 默认分解
            return self._default_decomposition(task)
    
    def _decompose_search_download(self, task: Task) -> List[str]:
        """分解搜索下载任务"""
        subtask_ids = []
        
        # 子任务1：分析查询
        analyze_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='analysis',
            description='分析搜索查询',
            instruction=f"分析并优化搜索查询: {task.instruction}",
            params={'original_query': task.instruction}
        )
        subtask_ids.append(analyze_id)
        
        # 子任务2：执行搜索
        search_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='web_search',
            description='执行网络搜索',
            instruction=f"搜索: {task.instruction}",
            params={'query': task.instruction}
        )
        subtask_ids.append(search_id)
        
        # 子任务3：筛选结果
        filter_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='analysis',
            description='筛选搜索结果',
            instruction=f"从搜索结果中筛选最相关的项目"
        )
        subtask_ids.append(filter_id)
        
        # 子任务4：下载资源
        download_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='download',
            description='下载选定资源',
            params={'destination': task.params.get('save_path', '~/Downloads')}
        )
        subtask_ids.append(download_id)
        
        # 子任务5：整理文件
        organize_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='file_organize',
            description='整理下载的文件',
            params={
                'source': task.params.get('save_path', '~/Downloads'),
                'target': task.params.get('storage_path', '~/Desktop/Papers')
            }
        )
        subtask_ids.append(organize_id)
        
        return subtask_ids
    
    def _decompose_file_organize(self, task: Task) -> List[str]:
        """分解文件整理任务"""
        subtask_ids = []
        
        # 子任务1：扫描文件
        scan_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='file_scan',
            description='扫描源目录文件',
            instruction=f"扫描目录: {task.params.get('source', '')}"
        )
        subtask_ids.append(scan_id)
        
        # 子任务2：分类文件
        classify_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='analysis',
            description='智能文件分类',
            instruction='使用AI分析并分类文件'
        )
        subtask_ids.append(classify_id)
        
        # 子任务3：移动文件
        move_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='file_move',
            description='移动文件到目标目录',
            params={
                'target': task.params.get('target', '')
            }
        )
        subtask_ids.append(move_id)
        
        # 子任务4：验证整理结果
        verify_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='verification',
            description='验证整理结果',
            instruction='确认所有文件已正确分类'
        )
        subtask_ids.append(verify_id)
        
        return subtask_ids
    
    def _decompose_web_operation(self, task: Task) -> List[str]:
        """分解网页操作任务"""
        subtask_ids = []
        
        # 子任务1：打开网页
        open_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='web_open',
            description='打开目标网页',
            params={'url': task.params.get('url', '')}
        )
        subtask_ids.append(open_id)
        
        # 子任务2：提取内容
        extract_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='web_extract',
            description='提取网页内容',
            instruction=f"提取关键信息: {task.instruction}"
        )
        subtask_ids.append(extract_id)
        
        # 子任务3：处理数据
        process_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='data_processing',
            description='处理提取的数据',
            instruction=f"数据处理: {task.instruction}"
        )
        subtask_ids.append(process_id)
        
        return subtask_ids
    
    def _decompose_complex_analysis(self, task: Task) -> List[str]:
        """分解复杂分析任务"""
        subtask_ids = []
        
        # 子任务1：信息收集
        collect_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='research',
            description='收集相关信息',
            instruction=f"研究主题: {task.instruction}"
        )
        subtask_ids.append(collect_id)
        
        # 子任务2：数据分析
        analyze_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='analysis',
            description='分析收集的信息',
            instruction='使用AI深度分析数据'
        )
        subtask_ids.append(analyze_id)
        
        # 子任务3：生成报告
        report_id = self.create_subtask(
            parent_task_id=task.id,
            task_type='report_generation',
            description='生成分析报告',
            instruction='根据分析结果生成结构化报告'
        )
        subtask_ids.append(report_id)
        
        return subtask_ids
    
    def _default_decomposition(self, task: Task) -> List[str]:
        """默认分解策略"""
        # 创建单个执行任务
        task_id = self.create_subtask(
            parent_task_id=task.id,
            task_type=task.type,
            description=task.description,
            instruction=task.instruction,
            params=task.params
        )
        
        return [task_id]
    
    def start_task(self, task_id: str) -> bool:
        """
        开始执行任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功开始
        """
        if task_id not in self.tasks:
            logger.error(f"任务不存在: {task_id}")
            return False
        
        task = self.tasks[task_id]
        
        # 检查依赖
        if not self._check_dependencies(task):
            task.status = TaskStatus.WAITING
            logger.info(f"任务等待依赖完成: {task_id}")
            return False
        
        # 检查执行器
        if task.type not in self.executors:
            logger.error(f"未注册任务执行器: {task.type}")
            task.status = TaskStatus.FAILED
            task.error = f"No executor for task type: {task.type}"
            return False
        
        # 更新状态
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().isoformat()
        self.current_task_id = task_id
        
        # 启动执行线程
        thread = threading.Thread(
            target=self._execute_task_thread,
            args=(task_id,),
            daemon=True
        )
        thread.start()
        self.execution_threads[task_id] = thread
        
        logger.info(f"任务已开始: {task_id}")
        return True
    
    def _execute_task_thread(self, task_id: str):
        """任务执行线程"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        try:
            # 获取执行器
            executor = self.executors.get(task.type)
            if executor:
                # 执行任务
                result = executor(task)
                task.result = result
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.COMPLETED
            
            # 标记完成时间
            task.completed_at = datetime.now().isoformat()
            
            # 通知依赖此任务的其他任务
            self._notify_dependents(task_id)
            
            logger.info(f"任务已完成: {task_id}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now().isoformat()
            logger.error(f"任务执行失败: {task_id} - {e}")
        
        finally:
            # 清理执行线程
            if task_id in self.execution_threads:
                del self.execution_threads[task_id]
            self.current_task_id = None
            self.task_completed_event.set()
    
    def _check_dependencies(self, task: Task) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                dep_task = self.tasks[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
        return True
    
    def _notify_dependents(self, completed_task_id: str):
        """通知依赖完成的任务"""
        dependents = self.dependency_graph.get(completed_task_id, [])
        
        for task_id in dependents:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status == TaskStatus.WAITING:
                    if self._check_dependencies(task):
                        self.start_task(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now().isoformat()
        
        logger.info(f"任务已取消: {task_id}")
        return True
    
    def retry_task(self, task_id: str) -> bool:
        """
        重试任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功重试
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if task.status == TaskStatus.FAILED:
            task.status = TaskStatus.PENDING
            task.error = None
            task.started_at = None
            task.completed_at = None
            
            return self.start_task(task_id)
        
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务信息"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """获取指定状态的所有任务"""
        return [t for t in self.tasks.values() if t.status == status]
    
    def get_tasks_by_type(self, task_type: str) -> List[Task]:
        """获取指定类型的所有任务"""
        return [t for t in self.tasks.values() if t.type == task_type]
    
    def get_pending_tasks(self) -> List[Task]:
        """获取所有待执行任务"""
        return [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
    
    def has_pending_tasks(self) -> bool:
        """检查是否有待执行任务"""
        return any(t.status == TaskStatus.PENDING for t in self.tasks.values())
    
    def get_next_task(self) -> Optional[Task]:
        """获取下一个要执行的任务（按优先级）"""
        pending = self.get_pending_tasks()
        
        if not pending:
            return None
        
        # 按优先级排序
        pending.sort(key=lambda t: t.priority.value)
        
        return pending[0]
    
    def get_pending_count(self) -> int:
        """获取待执行任务数量"""
        return len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
    
    def complete_task(self, task_id: str):
        """标记任务完成（手动调用）"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            self._notify_dependents(task_id)
    
    def fail_task(self, task_id: str, error: str):
        """标记任务失败"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.FAILED
            task.error = error
            task.completed_at = datetime.now().isoformat()
    
    def get_statistics(self) -> Dict:
        """获取任务统计信息"""
        total = len(self.tasks)
        
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len(
                self.get_tasks_by_status(status)
            )
        
        type_counts = {}
        for task_type in set(t.type for t in self.tasks.values()):
            type_counts[task_type] = len(self.get_tasks_by_type(task_type))
        
        return {
            'total_tasks': total,
            'status_distribution': status_counts,
            'type_distribution': type_counts,
            'running_tasks': len([
                t for t in self.tasks.values() 
                if t.status == TaskStatus.IN_PROGRESS
            ])
        }
    
    def clear_completed(self):
        """清除已完成的任务"""
        completed_ids = [
            t.id for t in self.tasks.values() 
            if t.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
        ]
        
        for task_id in completed_ids:
            self._remove_task(task_id)
        
        logger.info(f"已清除 {len(completed_ids)} 个已完成任务")
    
    def _remove_task(self, task_id: str):
        """移除任务"""
        if task_id in self.tasks:
            # 从依赖图中移除
            if task_id in self.dependency_graph:
                dependents = self.dependency_graph[task_id]
                for dep_id in dependents:
                    if dep_id in self.tasks:
                        task = self.tasks[dep_id]
                        if task_id in task.dependencies:
                            task.dependencies.remove(task_id)
                del self.dependency_graph[task_id]
            
            # 删除任务
            del self.tasks[task_id]
            
            # 删除保存的文件
            task_file = os.path.join(self.persistence_path, f"{task_id}.json")
            if os.path.exists(task_file):
                os.remove(task_file)
    
    def _save_task(self, task: Task):
        """保存任务到磁盘"""
        task_file = os.path.join(self.persistence_path, f"{task.id}.json")
        
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _load_tasks(self):
        """从磁盘加载任务"""
        if not os.path.exists(self.persistence_path):
            return
        
        try:
            for filename in os.listdir(self.persistence_path):
                if filename.endswith('.json'):
                    task_file = os.path.join(self.persistence_path, filename)
                    
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                        task = Task.from_dict(task_data)
                        self.tasks[task.id] = task
                        
                        # 加载依赖图
                        self.dependency_graph[task.id] = task.dependencies
            
            logger.info(f"已加载 {len(self.tasks)} 个任务")
            
        except Exception as e:
            logger.error(f"加载任务失败: {e}")
    
    def export_tasks(self, filepath: str):
        """导出任务列表"""
        tasks_data = [t.to_dict() for t in self.tasks.values()]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"任务已导出: {filepath}")
    
    def import_tasks(self, filepath: str):
        """导入任务列表"""
        with open(filepath, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        for task_data in tasks_data:
            task = Task.from_dict(task_data)
            self.tasks[task.id] = task
        
        logger.info(f"已导入 {len(tasks_data)} 个任务")


def create_task_planner(persistence_path: str = None) -> TaskPlanner:
    """创建任务规划器实例"""
    return TaskPlanner(persistence_path)
