#!/usr/bin/env python3
"""
作品管理 API
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
import os
import shutil
import json

from utils import (
    get_data_path, load_json, save_json, generate_id,
    list_dirs, delete_dir, ensure_dir
)

router = APIRouter()


def get_work_path(work_id: str) -> str:
    """获取作品路径"""
    return get_data_path("works", work_id)


@router.get("")
async def list_works():
    """列出所有作品"""
    base_path = get_data_path("works")
    work_ids = list_dirs(base_path)
    
    works = []
    for work_id in work_ids:
        meta_path = os.path.join(get_work_path(work_id), "meta.json")
        meta = load_json(meta_path)
        if meta:
            meta["id"] = work_id
            works.append(meta)
    
    return {"works": works}


@router.get("/{work_id}")
async def get_work(work_id: str):
    """获取作品详情"""
    meta_path = os.path.join(get_work_path(work_id), "meta.json")
    meta = load_json(meta_path)
    
    if not meta:
        raise HTTPException(status_code=404, detail="Work not found")
    
    meta["id"] = work_id
    return meta


@router.post("")
async def create_work(
    name: str = Form(...),
    description: str = Form("")
):
    """创建新作品"""
    work_id = generate_id()
    work_path = get_work_path(work_id)
    ensure_dir(work_path)
    
    # 创建默认元数据
    meta = {
        "name": name,
        "description": description,
        "cover_images": [],
        "style_description": "",
        "default_aspect_ratio": "16:9",
        "character_materials": [],
        "scene_materials": [],
        "prop_materials": []
    }
    
    meta_path = os.path.join(work_path, "meta.json")
    save_json(meta_path, meta)
    
    meta["id"] = work_id
    return meta


@router.put("/{work_id}")
async def update_work(
    work_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    style_description: Optional[str] = Form(None),
    default_aspect_ratio: Optional[str] = Form(None),
    cover_images: Optional[UploadFile] = File(None),
    character_materials: Optional[str] = Form(None),
    scene_materials: Optional[str] = Form(None),
    prop_materials: Optional[str] = Form(None)
):
    """更新作品详情"""
    work_path = get_work_path(work_id)
    meta_path = os.path.join(work_path, "meta.json")
    meta = load_json(meta_path)
    
    if not meta:
        raise HTTPException(status_code=404, detail="Work not found")
    
    # 初始化素材关联字段（如果不存在）
    if "character_materials" not in meta:
        meta["character_materials"] = []
    if "scene_materials" not in meta:
        meta["scene_materials"] = []
    if "prop_materials" not in meta:
        meta["prop_materials"] = []
    
    # 更新文本字段
    if name is not None:
        meta["name"] = name
    if description is not None:
        meta["description"] = description
    if style_description is not None:
        meta["style_description"] = style_description
    if default_aspect_ratio is not None:
        if default_aspect_ratio not in ["9:16", "16:9", "4:3", "3:4"]:
            raise HTTPException(status_code=400, detail="Invalid aspect ratio")
        meta["default_aspect_ratio"] = default_aspect_ratio
    
    # 更新素材关联字段
    if character_materials is not None:
        try:
            meta["character_materials"] = json.loads(character_materials)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid character_materials format")
    if scene_materials is not None:
        try:
            meta["scene_materials"] = json.loads(scene_materials)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid scene_materials format")
    if prop_materials is not None:
        try:
            meta["prop_materials"] = json.loads(prop_materials)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid prop_materials format")
    
    # 处理封面图片（支持多文件上传，通过多次调用或使用 Form 字段）
    # 注意：FastAPI 的 File 参数一次只能接收一个文件
    # 如果需要上传多个文件，前端需要多次调用或使用不同的字段名
    if cover_images:
        covers_dir = os.path.join(work_path, "covers")
        ensure_dir(covers_dir)
        
        cover_paths = meta.get("cover_images", [])
        cover_filename = f"cover_{len(cover_paths)}_{cover_images.filename}"
        cover_path = os.path.join(covers_dir, cover_filename)
        with open(cover_path, "wb") as f:
            shutil.copyfileobj(cover_images.file, f)
        cover_paths.append(f"covers/{cover_filename}")
        meta["cover_images"] = cover_paths
    
    save_json(meta_path, meta)
    
    meta["id"] = work_id
    return meta


@router.delete("/{work_id}")
async def delete_work(work_id: str):
    """删除作品"""
    work_path = get_work_path(work_id)
    
    if not os.path.exists(work_path):
        raise HTTPException(status_code=404, detail="Work not found")
    
    delete_dir(work_path)
    return {"message": "Work deleted"}

