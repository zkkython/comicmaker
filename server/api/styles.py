#!/usr/bin/env python3
"""
风格管理 API
提供风格的创建、编辑、删除和查询功能
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional, List, Dict, Any
import os
import shutil
import json

from utils import (
    get_data_path, load_json, save_json, generate_id,
    ensure_dir
)

router = APIRouter()

# 风格数据目录
def get_styles_path() -> str:
    """获取风格数据目录路径"""
    return get_data_path("styles")


def get_style_path(style_id: str) -> str:
    """获取单个风格的目录路径"""
    return os.path.join(get_styles_path(), style_id)


@router.get("")
async def get_styles():
    """获取所有风格列表"""
    styles_path = get_styles_path()
    if not os.path.exists(styles_path):
        return []
    
    styles = []
    for style_id in os.listdir(styles_path):
        style_dir = os.path.join(styles_path, style_id)
        if not os.path.isdir(style_dir):
            continue
        
        meta_path = os.path.join(style_dir, "meta.json")
        if not os.path.exists(meta_path):
            continue
        
        try:
            meta = load_json(meta_path)
            meta["id"] = style_id
            styles.append(meta)
        except Exception as e:
            print(f"加载风格 {style_id} 失败: {e}")
            continue
    
    # 按名称排序
    styles.sort(key=lambda x: x.get("name", ""))
    return styles


@router.get("/{style_id}")
async def get_style(style_id: str):
    """获取单个风格详情"""
    style_path = get_style_path(style_id)
    meta_path = os.path.join(style_path, "meta.json")
    
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="风格不存在")
    
    meta = load_json(meta_path)
    meta["id"] = style_id
    return meta


@router.get("/{style_id}/image/{filename}")
async def get_style_image(style_id: str, filename: str):
    """获取风格参考图片"""
    style_path = get_style_path(style_id)
    image_path = os.path.join(style_path, filename)
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="图片不存在")
    
    return FileResponse(
        image_path,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )


@router.post("")
async def create_style(
    name: str = Form(...),
    description: str = Form(...),
    reference_image: Optional[UploadFile] = File(None)
):
    """创建新风格"""
    style_id = generate_id()
    style_path = get_style_path(style_id)
    ensure_dir(style_path)
    
    # 保存参考图片
    reference_image_filename = None
    if reference_image:
        reference_image_filename = "reference.jpg"
        image_path = os.path.join(style_path, reference_image_filename)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(reference_image.file, f)
    
    # 保存元数据
    meta = {
        "name": name,
        "description": description,
        "reference_image": reference_image_filename
    }
    
    meta_path = os.path.join(style_path, "meta.json")
    save_json(meta_path, meta)
    
    meta["id"] = style_id
    return meta


@router.put("/{style_id}")
async def update_style(
    style_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    reference_image: Optional[UploadFile] = File(None)
):
    """更新风格"""
    style_path = get_style_path(style_id)
    meta_path = os.path.join(style_path, "meta.json")
    
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="风格不存在")
    
    meta = load_json(meta_path)
    
    # 更新字段
    if name is not None:
        meta["name"] = name
    if description is not None:
        meta["description"] = description
    
    # 更新参考图片
    if reference_image:
        reference_image_filename = "reference.jpg"
        image_path = os.path.join(style_path, reference_image_filename)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(reference_image.file, f)
        meta["reference_image"] = reference_image_filename
    
    save_json(meta_path, meta)
    
    meta["id"] = style_id
    return meta


@router.delete("/{style_id}")
async def delete_style(style_id: str):
    """删除风格"""
    style_path = get_style_path(style_id)
    
    if not os.path.exists(style_path):
        raise HTTPException(status_code=404, detail="风格不存在")
    
    # 删除整个风格目录
    shutil.rmtree(style_path)
    
    return {"success": True}

