#!/usr/bin/env python3
"""
异步任务管理 API
处理任务创建、状态查询、结果获取
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import os
import asyncio
from datetime import datetime
from enum import Enum

from utils import (
    get_data_path, load_json, save_json, generate_id,
    ensure_dir
)

router = APIRouter()

# 任务状态
class TaskStatus(str, Enum):
    PENDING = "pending"  # 请求中
    SUCCESS = "success"  # 成功
    FAILED = "failed"    # 失败


def get_task_path(task_id: str) -> str:
    """获取任务文件路径"""
    tasks_dir = get_data_path("tools", "tasks")
    ensure_dir(tasks_dir)
    return os.path.join(tasks_dir, f"{task_id}.json")


def create_task(tool_type: str, input_data: Dict[str, Any]) -> str:
    """创建任务"""
    task_id = generate_id()
    task = {
        "task_id": task_id,
        "tool_type": tool_type,
        "status": TaskStatus.PENDING.value,
        "input": input_data,
        "output": None,
        "error": None,
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    task_path = get_task_path(task_id)
    save_json(task_path, task)
    
    return task_id


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """获取任务"""
    task_path = get_task_path(task_id)
    return load_json(task_path)


def update_task_status(task_id: str, status: TaskStatus, output: Any = None, error: str = None, progress: int = None, api_request: Dict[str, Any] = None, prompt: str = None):
    """更新任务状态"""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task["status"] = status.value
    task["updated_at"] = datetime.now().isoformat()
    
    if output is not None:
        task["output"] = output
    if error is not None:
        task["error"] = error
    if progress is not None:
        task["progress"] = progress
    if api_request is not None:
        task["api_request"] = api_request
    if prompt is not None:
        task["prompt"] = prompt
    
    task_path = get_task_path(task_id)
    save_json(task_path, task)


@router.get("/{task_id}/status")
async def get_task_status(task_id: str):
    """查询任务状态"""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result = {
        "task_id": task_id,
        "status": task["status"],
        "progress": task.get("progress", 0),
        "error": task.get("error")
    }
    
    # 如果任务失败或正在处理，也返回输入数据以便前端显示
    if task["status"] in [TaskStatus.FAILED.value, TaskStatus.PENDING.value]:
        result["input"] = task.get("input")
        result["tool_type"] = task.get("tool_type")
        # 如果任务中有保存的 API 请求信息，也返回
        if "api_request" in task:
            result["api_request"] = task.get("api_request")
        if "prompt" in task:
            result["prompt"] = task.get("prompt")
    
    return result


@router.get("/{task_id}/result")
async def get_task_result(task_id: str):
    """获取任务结果"""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task["status"] != TaskStatus.SUCCESS.value:
        raise HTTPException(status_code=400, detail=f"任务尚未完成，当前状态：{task['status']}")
    
    return {
        "task_id": task_id,
        "tool_type": task["tool_type"],
        "input": task["input"],
        "output": task["output"]
    }

