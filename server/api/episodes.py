#!/usr/bin/env python3
"""
剧集管理 API
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import os
import shutil

from utils import (
    get_data_path, load_json, save_json, generate_id,
    list_dirs, delete_dir, ensure_dir
)

router = APIRouter()


def get_episode_path(work_id: str, episode_id: str) -> str:
    """获取剧集路径"""
    return get_data_path("works", work_id, "episodes", episode_id)


@router.get("/{work_id}")
async def list_episodes(work_id: str):
    """列出作品的所有剧集"""
    episodes_path = get_data_path("works", work_id, "episodes")
    episode_ids = list_dirs(episodes_path)
    
    episodes = []
    for episode_id in episode_ids:
        meta_path = os.path.join(get_episode_path(work_id, episode_id), "meta.json")
        meta = load_json(meta_path)
        if meta:
            meta["id"] = episode_id
            meta["work_id"] = work_id
            episodes.append(meta)
    
    return {"episodes": episodes}


@router.get("/{work_id}/{episode_id}")
async def get_episode(work_id: str, episode_id: str):
    """获取剧集详情"""
    meta_path = os.path.join(get_episode_path(work_id, episode_id), "meta.json")
    meta = load_json(meta_path)
    
    if not meta:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    meta["id"] = episode_id
    meta["work_id"] = work_id
    return meta


@router.post("/{work_id}")
async def create_episode(
    work_id: str,
    name: str = Form(...),
    description: str = Form("")
):
    """创建新剧集"""
    episode_id = generate_id()
    episode_path = get_episode_path(work_id, episode_id)
    ensure_dir(episode_path)
    
    # 创建默认元数据
    meta = {
        "name": name,
        "description": description,
        "cover_image": None
    }
    
    meta_path = os.path.join(episode_path, "meta.json")
    save_json(meta_path, meta)
    
    meta["id"] = episode_id
    meta["work_id"] = work_id
    return meta


@router.put("/{work_id}/{episode_id}")
async def update_episode(
    work_id: str,
    episode_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    cover_image: Optional[UploadFile] = File(None)
):
    """更新剧集详情"""
    episode_path = get_episode_path(work_id, episode_id)
    meta_path = os.path.join(episode_path, "meta.json")
    meta = load_json(meta_path)
    
    if not meta:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    # 更新文本字段
    if name is not None:
        meta["name"] = name
    if description is not None:
        meta["description"] = description
    
    # 处理封面图片
    if cover_image:
        cover_path = os.path.join(episode_path, "cover.jpg")
        with open(cover_path, "wb") as f:
            shutil.copyfileobj(cover_image.file, f)
        meta["cover_image"] = "cover.jpg"
    
    save_json(meta_path, meta)
    
    meta["id"] = episode_id
    meta["work_id"] = work_id
    return meta


@router.delete("/{work_id}/{episode_id}")
async def delete_episode(work_id: str, episode_id: str):
    """删除剧集"""
    episode_path = get_episode_path(work_id, episode_id)
    
    if not os.path.exists(episode_path):
        raise HTTPException(status_code=404, detail="Episode not found")
    
    delete_dir(episode_path)
    return {"message": "Episode deleted"}


@router.get("/{work_id}/{episode_id}/script")
async def get_script(work_id: str, episode_id: str):
    """获取脚本"""
    script_path = os.path.join(get_episode_path(work_id, episode_id), "script.json")
    script = load_json(script_path)
    
    if not script:
        return {"script": "", "expected_duration": 0}
    
    return script


@router.put("/{work_id}/{episode_id}/script")
async def save_script(
    work_id: str,
    episode_id: str,
    script: str = Form(...),
    expected_duration: float = Form(...),
    shot_duration: Optional[int] = Form(None)
):
    """保存脚本"""
    episode_path = get_episode_path(work_id, episode_id)
    script_path = os.path.join(episode_path, "script.json")
    
    script_data = {
        "script": script,
        "expected_duration": expected_duration
    }
    
    if shot_duration is not None:
        script_data["shot_duration"] = shot_duration
    
    save_json(script_path, script_data)
    return script_data


@router.get("/{work_id}/{episode_id}/storyboard")
async def get_storyboard(work_id: str, episode_id: str, format: Optional[str] = None):
    """获取分镜脚本"""
    storyboard_path = os.path.join(get_episode_path(work_id, episode_id), "storyboard.json")
    storyboard = load_json(storyboard_path)
    
    if not storyboard:
        # 向后兼容：如果没有 storyboard，返回空结构
        if format == "text":
            return {"text": "", "confirmed": False}
        return {"shots": [], "confirmed": False}
    
    # 向后兼容：如果只有 shots 字段，视为已确认
    if "confirmed" not in storyboard and "shots" in storyboard:
        storyboard["confirmed"] = True
    
    # 如果请求文本格式，只返回文本
    if format == "text":
        return {
            "text": storyboard.get("text", ""),
            "confirmed": storyboard.get("confirmed", False)
        }
    
    return storyboard


@router.post("/{work_id}/{episode_id}/storyboard/text")
async def save_storyboard_text(
    work_id: str,
    episode_id: str,
    text: str = Form(...)
):
    """保存分镜脚本文本"""
    episode_path = get_episode_path(work_id, episode_id)
    
    # 确保剧集目录存在
    if not os.path.exists(episode_path):
        raise HTTPException(status_code=404, detail="Episode not found")
    
    storyboard_path = os.path.join(episode_path, "storyboard.json")
    
    # 加载现有的 storyboard（如果有）
    storyboard = load_json(storyboard_path) or {}
    
    # 更新文本字段，但不改变 confirmed 状态
    storyboard["text"] = text
    if "confirmed" not in storyboard:
        storyboard["confirmed"] = False
    
    save_json(storyboard_path, storyboard)
    
    return {
        "text": text,
        "confirmed": storyboard.get("confirmed", False)
    }

