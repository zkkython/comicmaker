#!/usr/bin/env python3
"""
素材管理 API
包括人物角色、场景、道具的管理
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, Response, Response
from typing import List, Optional
import os
import shutil

from utils import (
    get_data_path, load_json, save_json, generate_id,
    list_dirs, delete_dir, ensure_dir
)

router = APIRouter()

MATERIAL_TYPES = ["characters", "scenes", "props", "others"]


def get_material_path(material_type: str, material_id: str) -> str:
    """获取素材路径"""
    return get_data_path("materials", material_type, material_id)


@router.get("/{material_type}")
async def list_materials(material_type: str):
    """列出指定类型的所有素材"""
    if material_type not in MATERIAL_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid material type: {material_type}")
    
    base_path = get_data_path("materials", material_type)
    material_ids = list_dirs(base_path)
    
    materials = []
    for material_id in material_ids:
        meta_path = os.path.join(get_material_path(material_type, material_id), "meta.json")
        meta = load_json(meta_path)
        if meta:
            meta["id"] = material_id
            materials.append(meta)
    
    return {"materials": materials}


@router.get("/{material_type}/{material_id}")
async def get_material(material_type: str, material_id: str):
    """获取单个素材详情"""
    if material_type not in MATERIAL_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid material type: {material_type}")
    
    meta_path = os.path.join(get_material_path(material_type, material_id), "meta.json")
    meta = load_json(meta_path)
    
    if not meta:
        raise HTTPException(status_code=404, detail="Material not found")
    
    meta["id"] = material_id
    return meta


@router.get("/{material_type}/{material_id}/image/{filename}")
async def get_material_image(material_type: str, material_id: str, filename: str):
    """获取素材图片（支持CORS）"""
    if material_type not in MATERIAL_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid material type: {material_type}")
    
    material_path = get_material_path(material_type, material_id)
    image_path = os.path.join(material_path, filename)
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    # 读取图片文件
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # 返回图片，并设置CORS头
    # 使用 no-cache 确保图片更新后能立即刷新
    return Response(
        content=image_data,
        media_type="image/jpeg",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )


@router.post("/{material_type}")
async def create_material(
    material_type: str,
    name: str = Form(...),
    description: str = Form(...),
    main_image: UploadFile = File(...),
    aux1_image: Optional[UploadFile] = File(None),
    aux2_image: Optional[UploadFile] = File(None)
):
    """创建新素材"""
    if material_type not in MATERIAL_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid material type: {material_type}")
    
    material_id = generate_id()
    material_path = get_material_path(material_type, material_id)
    ensure_dir(material_path)
    
    # 保存主图
    main_path = os.path.join(material_path, "main.jpg")
    with open(main_path, "wb") as f:
        shutil.copyfileobj(main_image.file, f)
    
    # 保存辅助图片
    aux_images = []
    for idx, aux_file in enumerate([aux1_image, aux2_image], 1):
        if aux_file:
            aux_path = os.path.join(material_path, f"aux{idx}.jpg")
            with open(aux_path, "wb") as f:
                shutil.copyfileobj(aux_file.file, f)
            aux_images.append(f"aux{idx}.jpg")
    
    # 保存元数据
    meta = {
        "name": name,
        "description": description,
        "main_image": "main.jpg",
        "aux_images": aux_images,
        "voice_settings": None  # 预留
    }
    
    meta_path = os.path.join(material_path, "meta.json")
    save_json(meta_path, meta)
    
    meta["id"] = material_id
    return meta


@router.put("/{material_type}/{material_id}")
async def update_material(
    material_type: str,
    material_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    main_image: Optional[UploadFile] = File(None),
    aux1_image: Optional[UploadFile] = File(None),
    aux2_image: Optional[UploadFile] = File(None)
):
    """更新素材"""
    if material_type not in MATERIAL_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid material type: {material_type}")
    
    material_path = get_material_path(material_type, material_id)
    meta_path = os.path.join(material_path, "meta.json")
    meta = load_json(meta_path)
    
    if not meta:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # 更新文本字段
    if name is not None:
        meta["name"] = name
    if description is not None:
        meta["description"] = description
    
    # 更新图片
    if main_image:
        main_path = os.path.join(material_path, "main.jpg")
        with open(main_path, "wb") as f:
            shutil.copyfileobj(main_image.file, f)
    
    aux_images = meta.get("aux_images", [])
    for idx, aux_file in enumerate([aux1_image, aux2_image], 1):
        if aux_file:
            aux_path = os.path.join(material_path, f"aux{idx}.jpg")
            with open(aux_path, "wb") as f:
                shutil.copyfileobj(aux_file.file, f)
            if f"aux{idx}.jpg" not in aux_images:
                aux_images.append(f"aux{idx}.jpg")
    
    meta["aux_images"] = aux_images
    save_json(meta_path, meta)
    
    meta["id"] = material_id
    return meta


@router.delete("/{material_type}/{material_id}")
async def delete_material(material_type: str, material_id: str):
    """删除素材"""
    if material_type not in MATERIAL_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid material type: {material_type}")
    
    material_path = get_material_path(material_type, material_id)
    
    if not os.path.exists(material_path):
        raise HTTPException(status_code=404, detail="Material not found")
    
    delete_dir(material_path)
    return {"message": "Material deleted"}

