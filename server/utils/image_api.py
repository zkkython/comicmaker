"""
图像生成 API 工具函数 - 使用 WavespeedClient 实现

此模块提供图像生成相关的便捷函数，内部统一使用 WavespeedClient。
所有函数保持向后兼容的签名。
"""

import logging
import os
from typing import List, Optional, Dict, Any

from .wavespeed_client import WavespeedClient, create_client_from_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 全局客户端实例（延迟加载）
_client = None


def _get_client(api_key: Optional[str] = None) -> WavespeedClient:
    """获取 WavespeedClient 实例"""
    global _client
    if api_key:
        return WavespeedClient(api_key=api_key)
    if _client is None:
        _client = create_client_from_config()
    return _client


def text_to_image_generate(
    api_key: str,
    prompt: str,
    model: str = "flux-kontext-pro",
    provider: str = "wavespeed-ai",
    aspect_ratio: str = "16:9",
    guidance_scale: float = 3.5,
    safety_tolerance: str = "5",
    num_images: int = 1
) -> str | None:
    """文生图"""
    client = _get_client(api_key)
    try:
        result = client.generate_image(
            prompt=prompt,
            model=model,
            provider=provider,
            aspect_ratio=aspect_ratio,
            guidance_scale=guidance_scale,
            safety_tolerance=safety_tolerance,
            num_images=num_images
        )
        return result.get('url') if result.get('success') else None
    except Exception as e:
        logger.error(f"Error in text_to_image_generate: {e}")
        return None


def image_to_image_generate(
    api_key,
    prompt,
    images,
    model="flux-kontext-pro",
    provider="wavespeed-ai",
    aspect_ratio="16:9",
    guidance_scale=3.5,
    safety_tolerance="5"
):
    """图生图"""
    client = _get_client(api_key)
    try:
        result = client.edit_image(
            prompt=prompt,
            images=images if isinstance(images, list) else [images],
            model=model,
            provider=provider,
            aspect_ratio=aspect_ratio,
            guidance_scale=guidance_scale,
            safety_tolerance=safety_tolerance
        )
        return result.get('url') if result.get('success') else None
    except Exception as e:
        logger.error(f"Error in image_to_image_generate: {e}")
        return None


def seedream_v4_5_text_to_image(
    api_key: str,
    prompt: str,
    size: str = "1024*1024",
    save_path: str = None
) -> Dict[str, Any]:
    """使用 seedream-v4.5 模型生成图片"""
    client = _get_client(api_key)
    try:
        result = client.generate_image(
            prompt=prompt,
            model="seedream-v4.5",
            provider="bytedance",
            size=size
        )
        if result.get('success') and save_path:
            import requests
            resp = requests.get(result['url'], stream=True)
            resp.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            result['output_path'] = save_path
        return result
    except Exception as e:
        logger.error(f"Error in seedream_v4_5_text_to_image: {e}")
        return {'success': False, 'error': str(e)}


def wan_2_6_text_to_image(
    api_key: str,
    prompt: str,
    size: str = "1024*1024",
    save_path: str = None
) -> Dict[str, Any]:
    """使用 wan-2.6 模型生成图片"""
    client = _get_client(api_key)
    try:
        result = client.generate_image(
            prompt=prompt,
            model="wan-2.6",
            provider="alibaba",
            size=size
        )
        if result.get('success') and save_path:
            import requests
            resp = requests.get(result['url'], stream=True)
            resp.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            result['output_path'] = save_path
        return result
    except Exception as e:
        logger.error(f"Error in wan_2_6_text_to_image: {e}")
        return {'success': False, 'error': str(e)}


def nano_banana_pro_text_to_image(
    api_key: str,
    prompt: str,
    aspect_ratio: str = "16:9",
    resolution: str = "1k",
    save_path: str = None
) -> Dict[str, Any]:
    """使用 nano-banana-pro 模型生成图片"""
    client = _get_client(api_key)
    try:
        result = client.generate_image(
            prompt=prompt,
            model="nano-banana-pro",
            provider="google",
            aspect_ratio=aspect_ratio,
            resolution=resolution
        )
        if result.get('success') and save_path:
            import requests
            resp = requests.get(result['url'], stream=True)
            resp.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            result['output_path'] = save_path
        return result
    except Exception as e:
        logger.error(f"Error in nano_banana_pro_text_to_image: {e}")
        return {'success': False, 'error': str(e)}


def seedream_v4_edit(
    api_key: str,
    prompt: str,
    image_urls: List[str],
    size: str = "1024*1024",
    enable_base64_output: bool = False,
    enable_sync_mode: bool = False,
    save_path: str = None
) -> Dict[str, Any]:
    """使用 seedream-v4.5 进行图生图"""
    client = _get_client(api_key)
    try:
        result = client.edit_image(
            prompt=prompt,
            images=image_urls,
            model="seedream-v4.5",
            provider="bytedance",
            size=size
        )
        if result.get('success') and save_path:
            import requests
            resp = requests.get(result['url'], stream=True)
            resp.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            result['output_path'] = save_path
        return result
    except Exception as e:
        logger.error(f"Error in seedream_v4_edit: {e}")
        return {'success': False, 'error': str(e)}


def wan_2_6_image_edit(
    api_key: str,
    prompt: str,
    image_urls: List[str],
    size: str = "1024*1024",
    save_path: str = None
) -> Dict[str, Any]:
    """使用 wan-2.6 进行图生图"""
    client = _get_client(api_key)
    try:
        result = client.edit_image(
            prompt=prompt,
            images=image_urls,
            model="wan-2.6",
            provider="alibaba",
            size=size
        )
        if result.get('success') and save_path:
            import requests
            resp = requests.get(result['url'], stream=True)
            resp.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            result['output_path'] = save_path
        return result
    except Exception as e:
        logger.error(f"Error in wan_2_6_image_edit: {e}")
        return {'success': False, 'error': str(e)}


def nano_banana_pro_edit(
    api_key: str,
    prompt: str,
    image_urls: List[str],
    aspect_ratio: str = "16:9",
    resolution: str = "1k",
    save_path: str = None
) -> Dict[str, Any]:
    """使用 nano-banana-pro 进行图生图"""
    client = _get_client(api_key)
    try:
        result = client.edit_image(
            prompt=prompt,
            images=image_urls,
            model="nano-banana-pro",
            provider="google",
            aspect_ratio=aspect_ratio,
            resolution=resolution
        )
        if result.get('success') and save_path:
            import requests
            resp = requests.get(result['url'], stream=True)
            resp.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            result['output_path'] = save_path
        return result
    except Exception as e:
        logger.error(f"Error in nano_banana_pro_edit: {e}")
        return {'success': False, 'error': str(e)}


# 辅助函数
def calculate_image_size(aspect_ratio: str, resolution: str) -> str:
    """计算图片尺寸"""
    if resolution == "1k":
        size_map = {
            "1:1": "2048*2048",
            "4:3": "2688*2016",
            "3:2": "2688*1792",
            "16:9": "2560*1440",
            "9:16": "1440*2560",
            "3:4": "2016*2688"
        }
    else:
        size_map = {
            "1:1": "4096*4096",
            "4:3": "3584*2688",
            "3:2": "3584*2389",
            "16:9": "3840*2160",
            "9:16": "2160*3840",
            "3:4": "2688*3584"
        }
    return size_map.get(aspect_ratio, "1024*1024")


def calculate_image_size_wan26(aspect_ratio: str, resolution: str) -> str:
    """为 wan2.6 模型计算图片尺寸"""
    ratio_parts = aspect_ratio.split(":")
    width_ratio = int(ratio_parts[0])
    height_ratio = int(ratio_parts[1])

    target_short = 768 if resolution == "1k" else 1024

    if width_ratio == height_ratio:
        size = min(max(target_short, 1024), 1440)
        width = height = size
    elif width_ratio < height_ratio:
        width = target_short
        height = int(target_short * height_ratio / width_ratio)
        if height > 1440:
            height = 1440
            width = int(height * width_ratio / height_ratio)
        if width < 768:
            width = 768
            height = int(width * height_ratio / width_ratio)
            if height > 1440:
                height = 1440
                width = int(height * width_ratio / height_ratio)
    else:
        height = target_short
        width = int(target_short * width_ratio / height_ratio)
        if width > 1440:
            width = 1440
            height = int(width * height_ratio / width_ratio)
        if height < 768:
            height = 768
            width = int(height * width_ratio / height_ratio)
            if width > 1440:
                width = 1440
                height = int(width * height_ratio / width_ratio)

    width = max(768, min(1440, width))
    height = max(768, min(1440, height))

    return f"{width}*{height}"


# 封装函数
def generate_image_to_image_seedream(
    api_key: str,
    prompt: str,
    images: List[str],
    aspect_ratio: str,
    resolution: str,
    save_path: str = None
) -> Dict[str, Any]:
    """使用 seedream-v4.5 进行图生图（封装函数）"""
    size = calculate_image_size(aspect_ratio, resolution)
    return seedream_v4_edit(api_key, prompt, images, size, save_path=save_path)


def generate_image_to_image_wan26(
    api_key: str,
    prompt: str,
    images: List[str],
    aspect_ratio: str,
    resolution: str,
    save_path: str = None
) -> Dict[str, Any]:
    """使用 wan-2.6 进行图生图（封装函数）"""
    size = calculate_image_size_wan26(aspect_ratio, resolution)
    return wan_2_6_image_edit(api_key, prompt, images, size, save_path=save_path)


def generate_image_to_image_nanopro(
    api_key: str,
    prompt: str,
    images: List[str],
    aspect_ratio: str,
    resolution: str,
    save_path: str = None
) -> Dict[str, Any]:
    """使用 nano-banana-pro 进行图生图（封装函数）"""
    return nano_banana_pro_edit(api_key, prompt, images, aspect_ratio, resolution, save_path)


def seedream_v4_sequential_edit(
    api_key: str,
    prompt: str,
    images: List[str],
    max_images: int = 2,
    size: str = "2048*2048",
    enable_base64_output: bool = False,
    enable_sync_mode: bool = False
) -> Dict[str, Any]:
    """
    Generate a series of magazine photoshoots using ByteDance seedream-v4 edit-sequential API.
    注：sequential edit 是特殊端点，直接使用底层 API
    """
    import json
    import time
    import requests
    from datetime import datetime

    client = _get_client(api_key)

    # 编码图片
    def encode_images(image_list):
        encoded = []
        for img in image_list:
            if img.startswith("http://") or img.startswith("https://"):
                encoded.append(img)
            elif img.startswith("data:image/"):
                encoded.append(img)
            elif os.path.exists(img):
                import base64
                ext = os.path.splitext(img)[1].lower()
                mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
                with open(img, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                encoded.append(f"data:{mime};base64,{b64}")
            elif img:
                encoded.append(img)
        return encoded

    b64_list = encode_images(images)
    padded_images = b64_list[:10]
    while len(padded_images) < 10:
        padded_images.append("")

    url = "https://api.wavespeed.ai/api/v3/bytedance/seedream-v4/edit-sequential"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "enable_base64_output": enable_base64_output,
        "enable_sync_mode": enable_sync_mode,
        "images": padded_images,
        "max_images": max_images,
        "prompt": prompt,
        "size": size
    }

    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        return {'success': False, 'error': f"Error: {response.status_code}, {response.text}"}

    result = response.json()["data"]
    request_id = result["id"]
    logger.info(f"Task submitted. Request ID: {request_id}")

    # 轮询结果
    poll_url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    while True:
        poll_response = requests.get(poll_url, headers={"Authorization": f"Bearer {api_key}"})
        if poll_response.status_code == 200:
            data = poll_response.json()["data"]
            status = data.get("status")
            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin:.2f}s")
                return {
                    'success': True,
                    'output_path': data["outputs"],
                    'message': "Image editing completed successfully."
                }
            elif status == "failed":
                return {'success': False, 'error': f"Task failed: {data.get('error')}"}
            else:
                logger.info(f"Task still processing. Status: {status}")
                time.sleep(0.5)
        else:
            return {'success': False, 'error': f"Error: {poll_response.status_code}"}
