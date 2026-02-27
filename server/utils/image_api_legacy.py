import requests
import json
import time
import logging
import os
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional

from .wavespeed_client import WavespeedClient, create_client_from_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()

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


def text_to_image_generate(api_key : str, prompt : str, model: str="flux-kontext-pro", provider: str="wavespeed-ai", aspect_ratio: str="16:9", guidance_scale: float=3.5, safety_tolerance: str="5", num_images: int=1) -> str | None:
    """文生图 - 使用 WavespeedClient 内部实现"""
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
        return {'success': False, 'error': str(e)}


def image_to_image_generate(api_key, prompt, images, model="flux-kontext-pro", provider="wavespeed-ai", aspect_ratio="16:9", guidance_scale=3.5, safety_tolerance="5"):
    """图生图 - 使用 WavespeedClient 内部实现"""
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
        return result.get('url') if result.get('success') else {'success': False, 'error': 'Failed'}
    except Exception as e:
        logger.error(f"Error in image_to_image_generate: {e}")
        return {'success': False, 'error': str(e)}


def seedream_v4_sequential_edit(api_key: str, prompt: str, images: list[str], max_images: int = 2, size: str = "2048*2048", enable_base64_output: bool = False, enable_sync_mode: bool = False):
    """
    Generate a series of magazine photoshoots using ByteDance seedream-v4 edit-sequential API.
    
    Args:
        api_key: WaveSpeed API key
        prompt: Text prompt for image generation
        images: List of image URLs (up to 10, empty strings for unused slots)
        max_images: Maximum number of images to generate
        size: Output image size
        enable_base64_output: Whether to return base64 encoded output
        enable_sync_mode: Whether to use synchronous mode
    
    Returns:
        dict: Result containing success status and output URL or error message
    """
    # 使用统一的编码函数处理图片（Convert local image paths to base64 encoded data URIs）
    b64_list, _ = _encode_images_to_base64(images)
    
    # 对于 sequential edit，需要填充到10个位置（空字符串用于未使用的槽位）
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
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }

    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]

            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                output_url = result["outputs"]
                logger.info(f"Task completed. URL: {output_url}")
                return {
                    'success': True,
                    'output_path': output_url,
                    'message': "Image editing completed successfully."
                }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }


def seedream_v4_edit(api_key: str, prompt: str, image_urls: list[str], size: str = "1024*1024", enable_base64_output: bool = False, enable_sync_mode: bool = False, save_path: str = None):
    """
    使用 seedream-v4.5 模型进行图生图（只支持 URL，不支持 base64）
    
    Args:
        api_key: Wavespeed API 密钥
        prompt: 图片生成提示词
        image_urls: 图片 URL 列表（OSS URL）
        size: 图片尺寸
        enable_base64_output: 是否启用 base64 输出
        enable_sync_mode: 是否启用同步模式
        save_path: 可选，保存路径
    """
    url = "https://api.wavespeed.ai/api/v3/bytedance/seedream-v4.5/edit"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    # 直接使用 URL 列表，不转换为 base64
    image_list = image_urls[:10]
    
    payload = {
        "enable_base64_output": enable_base64_output,
        "enable_sync_mode": enable_sync_mode,
        "images": image_list,  # 直接使用 URL
        "prompt": prompt,
        "size": size
    }

    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }

    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]

            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                image_url = result["outputs"][0]
                logger.info(f"Task completed. URL: {image_url}")
                
                # 保存完整的 API 响应
                full_response = response.json()
                
                # 下载图片（如果提供了 save_path）
                if save_path:
                    resp = requests.get(image_url, stream=True)
                    resp.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                    return {
                        'success': True,
                        'output_path': save_path,
                        'url': image_url,
                        'message': "Image editing completed successfully.",
                        'response_data': full_response
                    }
                else:
                    return {
                        'success': True,
                        'output_path': image_url,
                        'url': image_url,
                        'message': "Image editing completed successfully.",
                        'response_data': full_response
                    }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }


def calculate_image_size(aspect_ratio: str, resolution: str) -> str:
    """
    根据比例和分辨率计算图片尺寸（宽*高格式）
    使用提升后的分辨率设置
    
    Args:
        aspect_ratio: 比例，可选值：1:1, 3:4, 4:3, 16:9, 9:16
        resolution: 分辨率，可选值：1k, 2k
    
    Returns:
        str: 尺寸字符串，格式："宽*高"，例如 "2048*2048"
    """
    # 根据用户提供的建议分辨率映射
    # 1k 分辨率使用较低值，2k 分辨率使用较高值
    if resolution == "1k":
        # 1k 分辨率映射
        size_map = {
            "1:1": "2048*2048",
            "4:3": "2688*2016",
            "3:2": "2688*1792",
            "16:9": "2560*1440",
            "9:16": "1440*2560",
            "3:4": "2016*2688"
        }
    else:  # 2k 或更高
        # 2k 分辨率映射（使用更高的值）
        size_map = {
            "1:1": "4096*4096",  # Square 4K
            "4:3": "3584*2688",  # 按比例放大
            "3:2": "3584*2389",  # 按比例放大
            "16:9": "3840*2160",  # 4K UHD
            "9:16": "2160*3840",  # 竖版 4K
            "3:4": "2688*3584"   # 按比例放大
        }
    
    # 如果映射中存在，直接返回
    if aspect_ratio in size_map:
        return size_map[aspect_ratio]
    
    # 如果不在映射中，使用旧的计算方式作为后备
    short_edge = 2048 if resolution == "1k" else 4096
    ratio_parts = aspect_ratio.split(":")
    width_ratio = int(ratio_parts[0])
    height_ratio = int(ratio_parts[1])
    
    if width_ratio == height_ratio:  # 1:1
        width = height = short_edge
    elif width_ratio < height_ratio:  # 3:4, 9:16 (竖图，短边是宽)
        width = short_edge
        height = int(short_edge * height_ratio / width_ratio)
    else:  # 4:3, 16:9 (横图，短边是高)
        height = short_edge
        width = int(short_edge * width_ratio / height_ratio)
    
    return f"{width}*{height}"


def calculate_image_size_wan26(aspect_ratio: str, resolution: str) -> str:
    """
    为 wan2.6 模型计算图片尺寸（宽*高格式）
    wan2.6 的像素范围限制在 768 ~ 1440 per dimension
    
    Args:
        aspect_ratio: 比例，可选值：1:1, 3:4, 4:3, 16:9, 9:16
        resolution: 分辨率，可选值：1k, 2k
    
    Returns:
        str: 尺寸字符串，格式："宽*高"，例如 "1024*1024"
    """
    # 解析比例
    ratio_parts = aspect_ratio.split(":")
    width_ratio = int(ratio_parts[0])
    height_ratio = int(ratio_parts[1])
    
    # 根据分辨率确定目标短边长度
    # 1k: 使用较小的值（768）
    # 2k: 使用较大的值（1024，接近但不超过 1440）
    if resolution == "1k":
        target_short = 768
    else:  # 2k
        target_short = 1024
    
    # 计算宽高
    if width_ratio == height_ratio:  # 1:1
        # 正方形：使用目标值，但限制在 768-1440 范围内
        size = min(max(target_short, 1024), 1440)
        width = height = size
    elif width_ratio < height_ratio:  # 3:4, 9:16 (竖图，短边是宽)
        width = target_short
        height = int(target_short * height_ratio / width_ratio)
        # 如果高度超过 1440，按比例缩小
        if height > 1440:
            height = 1440
            width = int(height * width_ratio / height_ratio)
        # 确保宽度不小于 768
        if width < 768:
            width = 768
            height = int(width * height_ratio / width_ratio)
            # 如果高度又超过 1440，再次调整
            if height > 1440:
                height = 1440
                width = int(height * width_ratio / height_ratio)
    else:  # 4:3, 16:9 (横图，短边是高)
        height = target_short
        width = int(target_short * width_ratio / height_ratio)
        # 如果宽度超过 1440，按比例缩小
        if width > 1440:
            width = 1440
            height = int(width * height_ratio / width_ratio)
        # 确保高度不小于 768
        if height < 768:
            height = 768
            width = int(height * width_ratio / height_ratio)
            # 如果宽度又超过 1440，再次调整
            if width > 1440:
                width = 1440
                height = int(width * height_ratio / width_ratio)
    
    # 最终确保两个维度都在 768-1440 范围内
    width = max(768, min(1440, width))
    height = max(768, min(1440, height))
    
    return f"{width}*{height}"


def seedream_v4_5_text_to_image(api_key: str, prompt: str, size: str = "1024*1024", save_path: str = None):
    """
    使用 seedream-v4 模型生成图片（文生图）
    
    Args:
        api_key: Wavespeed API 密钥
        prompt: 图片生成提示词
        size: 图片尺寸，格式："宽*高"，例如 "1024*1024"
        save_path: 可选，保存路径
    
    Returns:
        dict: 包含 success, output_path/error 的字典
    """
    url = "https://api.wavespeed.ai/api/v3/bytedance/seedream-v4.5"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    seed = int(datetime.now().timestamp())
    payload = {
        "prompt": prompt,
        "size": size,
        "seed": seed
    }
    
    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }
    
    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]
            
            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                image_url = result["outputs"][0]
                logger.info(f"Task completed. URL: {image_url}")
                
                # 保存完整的 API 响应
                full_response = response.json()
                
                # 下载图片
                if save_path:
                    resp = requests.get(image_url, stream=True)
                    resp.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                    return {
                        'success': True,
                        'output_path': save_path,
                        'url': image_url,
                        'message': "Image generated successfully.",
                        'response_data': full_response
                    }
                else:
                    return {
                        'success': True,
                        'output_path': image_url,
                        'url': image_url,
                        'message': "Image generated successfully.",
                        'response_data': full_response
                    }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }
        time.sleep(2)


def wan_2_6_text_to_image(api_key: str, prompt: str, size: str = "1024*1024", save_path: str = None):
    """
    使用 wan-2.6 模型生成图片
    
    Args:
        api_key: Wavespeed API 密钥
        prompt: 图片生成提示词
        size: 图片尺寸，格式："宽*高"，例如 "1024*1024"
        save_path: 可选，保存路径
    
    Returns:
        dict: 包含 success, output_path/error 的字典
    """
    url = "https://api.wavespeed.ai/api/v3/alibaba/wan-2.6/text-to-image"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    seed = int(datetime.now().timestamp())
    payload = {
        "prompt": prompt,
        "size": size,
        "seed": seed
    }
    
    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }
    
    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]
            
            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                image_url = result["outputs"][0]
                logger.info(f"Task completed. URL: {image_url}")
                
                # 保存完整的 API 响应
                full_response = response.json()
                
                # 下载图片
                if save_path:
                    resp = requests.get(image_url, stream=True)
                    resp.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                    return {
                        'success': True,
                        'output_path': save_path,
                        'url': image_url,
                        'message': "Image generated successfully.",
                        'response_data': full_response
                    }
                else:
                    return {
                        'success': True,
                        'output_path': image_url,
                        'url': image_url,
                        'message': "Image generated successfully.",
                        'response_data': full_response
                    }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }
        time.sleep(2)


def nano_banana_pro_text_to_image(api_key: str, prompt: str, aspect_ratio: str = "16:9", resolution: str = "1k", save_path: str = None):
    """
    使用 nano-banana-pro 模型生成图片
    
    Args:
        api_key: Wavespeed API 密钥
        prompt: 图片生成提示词
        aspect_ratio: 比例，例如 "16:9"
        resolution: 分辨率，可选值：1k, 2k
        save_path: 可选，保存路径
    
    Returns:
        dict: 包含 success, output_path/error 的字典
    """
    url = "https://api.wavespeed.ai/api/v3/google/nano-banana-pro/text-to-image"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    seed = int(datetime.now().timestamp())
    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "seed": seed
    }
    
    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }
    
    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]
            
            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                image_url = result["outputs"][0]
                logger.info(f"Task completed. URL: {image_url}")
                
                # 保存完整的 API 响应
                full_response = response.json()
                
                # 下载图片
                if save_path:
                    resp = requests.get(image_url, stream=True)
                    resp.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                    return {
                        'success': True,
                        'output_path': save_path,
                        'url': image_url,
                        'message': "Image generated successfully.",
                        'response_data': full_response
                    }
                else:
                    return {
                        'success': True,
                        'output_path': image_url,
                        'url': image_url,
                        'message': "Image generated successfully.",
                        'response_data': full_response
                    }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }
        time.sleep(2)


def _encode_single_image_to_base64(image_path: str) -> str:
    """
    将单个图片文件编码为 base64 data URI（参考 query_llm.py 的实现）
    
    Args:
        image_path: 图片文件路径
    
    Returns:
        str: base64 data URI 字符串
    
    Raises:
        FileNotFoundError: 图片文件不存在
        ValueError: 不支持的图片格式
        RuntimeError: 编码失败
    """
    try:
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mime_type = mime_types.get(ext)
        if not mime_type:
            raise ValueError(f"不支持的图片格式: {ext}")

        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded_string}"
    except FileNotFoundError:
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    except Exception as e:
        raise RuntimeError(f"图片编码失败 {image_path}: {e}")


def _encode_images_to_base64(images: list[str]) -> tuple[list[str], list[str]]:
    """
    将图片路径列表或 URL 列表编码为 base64 data URI 列表（优化版本，使用统一的编码函数）
    
    Args:
        images: 图片路径列表、URL 列表或 base64 字符串列表
    
    Returns:
        tuple[list[str], list[str]]: (base64 data URI 列表, 简化显示列表)
    """
    import tempfile
    import requests as req_lib
    
    b64_list = []
    simplified_list = []
    for image in images:
        if not image:
            continue
            
        # 如果已经是 base64 data URI 字符串，直接使用
        if image.startswith("data:image/"):
            b64_list.append(image)
            # 尝试提取长度信息用于日志
            if "base64," in image:
                base64_part = image.split("base64,")[1]
                simplified_list.append(f"data:image/...base64,{len(base64_part)} chars")
            else:
                simplified_list.append(image[:50] + "..." if len(image) > 50 else image)
        elif image.startswith("http://") or image.startswith("https://"):
            # 如果是 URL，先下载图片，然后转换为 base64
            try:
                logger.info(f"从 URL 下载图片: {image}")
                response = req_lib.get(image, timeout=30)
                response.raise_for_status()
                
                # 创建临时文件保存下载的图片
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name
                
                try:
                    # 使用统一的编码函数
                    b64_data_uri = _encode_single_image_to_base64(tmp_path)
                    b64_list.append(b64_data_uri)
                    # 提取 base64 部分用于简化显示
                    if "base64," in b64_data_uri:
                        base64_part = b64_data_uri.split("base64,")[1]
                        simplified_list.append(f"URL->base64,{len(base64_part)} chars")
                    else:
                        simplified_list.append(b64_data_uri[:50] + "..." if len(b64_data_uri) > 50 else b64_data_uri)
                finally:
                    # 清理临时文件
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
            except Exception as e:
                logger.error(f"从 URL 下载图片失败: {image}, 错误: {e}")
                # 跳过失败的图片，继续处理其他图片
                continue
        elif os.path.exists(image):
            # 如果是文件路径，使用统一的编码函数
            try:
                b64_data_uri = _encode_single_image_to_base64(image)
                b64_list.append(b64_data_uri)
                # 提取 base64 部分用于简化显示
                if "base64," in b64_data_uri:
                    base64_part = b64_data_uri.split("base64,")[1]
                    simplified_list.append(f"data:image/...base64,{len(base64_part)} chars")
                else:
                    simplified_list.append(b64_data_uri[:50] + "..." if len(b64_data_uri) > 50 else b64_data_uri)
            except Exception as e:
                logger.error(f"图片编码失败: {image}, 错误: {e}")
                # 跳过失败的图片，继续处理其他图片
                continue
        else:
            # 既不是 base64 字符串，也不是有效路径或 URL，记录警告但继续处理
            logger.warning(f"无效的图片输入: {image}")
            # 仍然添加到列表中，让 API 处理错误
            b64_list.append(image)
            simplified_list.append(f"无效输入: {image[:50]}...")
    
    # 最多10张图片
    return b64_list[:10], simplified_list[:10]


def generate_image_to_image_seedream(
    api_key: str,
    prompt: str,
    images: list[str],
    aspect_ratio: str,
    resolution: str,
    save_path: str = None
) -> dict:
    """
    使用 seedream-v4.5 模型进行图生图（封装函数，返回完整的请求/响应信息）
    
    Args:
        api_key: Wavespeed API 密钥
        prompt: 图片生成提示词
        images: 图片 URL 列表（OSS URL）
        aspect_ratio: 比例，例如 "16:9"
        resolution: 分辨率，可选值：1k, 2k
        save_path: 可选，保存路径
    
    Returns:
        dict: 包含 success, output_path, url, api_request, api_response 的字典
    """
    # 计算尺寸
    size = calculate_image_size(aspect_ratio, resolution)
    
    # 直接使用 URL 列表（不再转换为 base64）
    image_list = images[:10]  # 最多10张图片
    
    # 构建请求 payload（用于 api_request）
    seed = int(datetime.now().timestamp())
    payload_for_log = {
        "prompt": prompt,
        "images": image_list,  # 直接使用 URL
        "size": size,
        "seed": seed
    }
    
    # 调用底层 API（传入 URL 列表）
    result = seedream_v4_edit(
        api_key, prompt, image_list, size, False, False, save_path
    )
    
    if not result.get('success'):
        return result
    
    # 构建完整的返回信息
    api_request = {
        "url": "https://api.wavespeed.ai/api/v3/bytedance/seedream-v4.5/edit",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer ***"
        },
        "payload": payload_for_log
    }
    
    return {
        'success': True,
        'output_path': result.get('output_path'),
        'url': result.get('url'),
        'message': result.get('message'),
        'api_request': api_request,
        'api_response': result.get('response_data', {})
    }


def generate_image_to_image_wan26(
    api_key: str,
    prompt: str,
    images: list[str],
    aspect_ratio: str,
    resolution: str,
    save_path: str = None
) -> dict:
    """
    使用 wan-2.6 模型进行图生图（封装函数，返回完整的请求/响应信息）
    
    Args:
        api_key: Wavespeed API 密钥
        prompt: 图片生成提示词
        images: 图片路径列表
        aspect_ratio: 比例，例如 "16:9"
        resolution: 分辨率，可选值：1k, 2k
        save_path: 可选，保存路径
    
    Returns:
        dict: 包含 success, output_path, url, api_request, api_response 的字典
    """
    # 计算尺寸
    size = calculate_image_size_wan26(aspect_ratio, resolution)
    
    # 直接使用 URL 列表（不再转换为 base64）
    image_list = images[:10]  # 最多10张图片
    
    # 构建请求 payload（用于 api_request）
    seed = int(datetime.now().timestamp())
    payload_for_log = {
        "prompt": prompt,
        "images": image_list,  # 直接使用 URL
        "size": size,
        "seed": seed
    }
    
    # 调用底层 API（传入 URL 列表）
    result = wan_2_6_image_edit(
        api_key, prompt, image_list, size, save_path
    )
    
    if not result.get('success'):
        return result
    
    # 构建完整的返回信息
    api_request = {
        "url": "https://api.wavespeed.ai/api/v3/alibaba/wan-2.6/image-edit",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer ***"
        },
        "payload": payload_for_log
    }
    
    return {
        'success': True,
        'output_path': result.get('output_path'),
        'url': result.get('url'),
        'message': result.get('message'),
        'api_request': api_request,
        'api_response': result.get('response_data', {})
    }


def generate_image_to_image_nanopro(
    api_key: str,
    prompt: str,
    images: list[str],
    aspect_ratio: str,
    resolution: str,
    save_path: str = None
) -> dict:
    """
    使用 nano-banana-pro 模型进行图生图（封装函数，返回完整的请求/响应信息）
    
    Args:
        api_key: Wavespeed API 密钥
        prompt: 图片生成提示词
        images: 图片路径列表
        aspect_ratio: 比例，例如 "16:9"
        resolution: 分辨率，可选值：1k, 2k
        save_path: 可选，保存路径
    
    Returns:
        dict: 包含 success, output_path, url, api_request, api_response 的字典
    """
    # 直接使用 URL 列表（不再转换为 base64）
    image_list = images[:10]  # 最多10张图片
    
    # 构建请求 payload（用于 api_request）
    seed = int(datetime.now().timestamp())
    payload_for_log = {
        "prompt": prompt,
        "images": image_list,  # 直接使用 URL
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "seed": seed
    }
    
    # 调用底层 API（传入 URL 列表）
    result = nano_banana_pro_edit(
        api_key, prompt, image_list, aspect_ratio, resolution, save_path
    )
    
    if not result.get('success'):
        return result
    
    # 构建完整的返回信息
    api_request = {
        "url": "https://api.wavespeed.ai/api/v3/google/nano-banana-pro/edit",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer ***"
        },
        "payload": payload_for_log
    }
    
    return {
        'success': True,
        'output_path': result.get('output_path'),
        'url': result.get('url'),
        'message': result.get('message'),
        'api_request': api_request,
        'api_response': result.get('response_data', {})
    }


def wan_2_6_image_edit(api_key: str, prompt: str, image_urls: list[str], size: str = "1024*1024", save_path: str = None):
    """
    使用 wan-2.6 模型进行图生图（只支持 URL，不支持 base64）
    
    Args:
        api_key: Wavespeed API 密钥
        prompt: 图片生成提示词
        image_urls: 图片 URL 列表（OSS URL）
        size: 图片尺寸，格式："宽*高"，例如 "1024*1024"
        save_path: 可选，保存路径
    
    Returns:
        dict: 包含 success, output_path/error 的字典
    """
    url = "https://api.wavespeed.ai/api/v3/alibaba/wan-2.6/image-edit"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    # 直接使用 URL 列表，不转换为 base64
    image_list = image_urls[:10]  # 最多10张图片
    
    seed = int(datetime.now().timestamp())
    payload = {
        "prompt": prompt,
        "images": image_list,
        "size": size,
        "seed": seed
    }
    
    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }
    
    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]
            
            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                image_url = result["outputs"][0]
                logger.info(f"Task completed. URL: {image_url}")
                
                # 保存完整的 API 响应
                full_response = response.json()
                
                # 下载图片
                if save_path:
                    resp = requests.get(image_url, stream=True)
                    resp.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                    return {
                        'success': True,
                        'output_path': save_path,
                        'url': image_url,
                        'message': "Image editing completed successfully.",
                        'response_data': full_response
                    }
                else:
                    return {
                        'success': True,
                        'output_path': image_url,
                        'url': image_url,
                        'message': "Image editing completed successfully.",
                        'response_data': full_response
                    }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }
        time.sleep(2)


def nano_banana_pro_edit(api_key: str, prompt: str, image_urls: list[str], aspect_ratio: str = "16:9", resolution: str = "1k", save_path: str = None):
    """
    使用 nano-banana-pro 模型进行图生图（只支持 URL，不支持 base64）
    
    Args:
        api_key: Wavespeed API 密钥
        prompt: 图片生成提示词
        image_urls: 图片 URL 列表（OSS URL）
        aspect_ratio: 比例，例如 "16:9"
        resolution: 分辨率，可选值：1k, 2k
        save_path: 可选，保存路径
    
    Returns:
        dict: 包含 success, output_path/error 的字典
    """
    url = "https://api.wavespeed.ai/api/v3/google/nano-banana-pro/edit"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    # 直接使用 URL 列表，不转换为 base64
    image_list = image_urls[:10]  # 最多10张图片
    
    seed = int(datetime.now().timestamp())
    payload = {
        "prompt": prompt,
        "images": image_list,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "seed": seed
    }
    
    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }
    
    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]
            
            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                image_url = result["outputs"][0]
                logger.info(f"Task completed. URL: {image_url}")
                
                # 保存完整的 API 响应
                full_response = response.json()
                
                # 下载图片
                if save_path:
                    resp = requests.get(image_url, stream=True)
                    resp.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                    return {
                        'success': True,
                        'output_path': save_path,
                        'url': image_url,
                        'message': "Image editing completed successfully.",
                        'response_data': full_response
                    }
                else:
                    return {
                        'success': True,
                        'output_path': image_url,
                        'url': image_url,
                        'message': "Image editing completed successfully.",
                        'response_data': full_response
                    }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }
        time.sleep(2)

