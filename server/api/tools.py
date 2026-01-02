#!/usr/bin/env python3
"""
AI 工具 API
提供8个AI工具的接口
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from enum import Enum
import os
import asyncio
import shutil
import yaml
import requests
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from utils import (
    get_data_path, load_json, save_json, generate_id,
    ensure_dir
)
from api.tasks import create_task, update_task_status, TaskStatus
from utils.wavespeed_api import (
    calculate_image_size,
    seedream_v4_5_text_to_image,
    wan_2_6_text_to_image,
    nano_banana_pro_text_to_image,
    vidu_reference_to_video_q2,
    sora_2_image_to_video,
    wan_2_5_image_to_video,
    wan_2_6_image_to_video,
)
from utils.image_api import (
    generate_image_to_image_seedream,
    generate_image_to_image_wan26,
    generate_image_to_image_nanopro,
)
from utils.image_process import download_image, download_video

router = APIRouter()

# 工具类型
class ToolType(str, Enum):
    GENERATE_SCRIPT = "generate_script"  # 生成剧本
    GENERATE_SINGLE_SHOT_STORYBOARD = "generate_single_shot_storyboard"  # 生成单镜头分镜脚本
    GENERATE_STORYBOARD = "generate_storyboard"  # 生成分镜脚本（保留兼容性）
    GENERATE_SHOT_PROMPTS = "generate_shot_prompts"  # 生成分镜提示词
    IMAGE_TO_DESCRIPTION = "image_to_description"  # 图生描述
    IMAGE_TO_STYLE_DESCRIPTION = "image_to_style_description"  # 图生风格描述
    TEXT_TO_IMAGE = "text_to_image"  # 文生图
    IMAGE_TO_IMAGE = "image_to_image"  # 图生图
    VIDU_REF_IMAGE_TO_VIDEO = "vidu_ref_image_to_video"  # vidu参考生视频
    SORA_IMAGE_TO_VIDEO = "sora_image_to_video"  # sora生视频
    WAN_IMAGE_TO_VIDEO = "wan_image_to_video"  # wan图生视频
    KEYFRAME_TO_VIDEO = "keyframe_to_video"  # 首尾帧生视频
    TEXT_TO_AUDIO = "text_to_audio"  # 生音频


def get_history_path(record_id: str) -> str:
    """获取历史记录文件路径"""
    history_dir = get_data_path("tools", "history")
    ensure_dir(history_dir)
    return os.path.join(history_dir, f"{record_id}.json")


def get_output_path(tool_type: str, output_id: str) -> str:
    """获取输出文件目录路径"""
    return get_data_path("tools", "outputs", tool_type, output_id)


def create_history_record(task_id: str, tool_type: str, input_data: Dict[str, Any], output_data: Any) -> str:
    """创建历史记录"""
    record_id = generate_id()
    record = {
        "record_id": record_id,
        "task_id": task_id,
        "tool_type": tool_type,
        "input": input_data,
        "output": output_data,
        "created_at": datetime.now().isoformat()
    }
    
    history_path = get_history_path(record_id)
    save_json(history_path, record)
    
    return record_id


# 提示词加载和变量替换函数
def load_prompt_template(template_path: str) -> str:
    """
    加载提示词模板文件
    
    Args:
        template_path: 模板文件路径
        
    Returns:
        模板内容字符串
        
    Raises:
        FileNotFoundError: 文件不存在时抛出
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"提示词模板文件不存在: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def replace_prompt_variables(template: str, **kwargs) -> str:
    """
    替换提示词模板中的变量
    
    Args:
        template: 模板字符串
        **kwargs: 变量名和值的映射
        
    Returns:
        替换后的字符串
    """
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def load_llm_config() -> Dict[str, str]:
    """
    从 config.yaml 加载 LLM 配置
    
    Returns:
        {
            "model": "openai/gpt-4o",
            "api_key": "..."
        }
        
    Raises:
        FileNotFoundError: 配置文件不存在时抛出
        KeyError: 配置项缺失时抛出
    """
    # 获取配置文件路径
    server_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(server_dir, "config", "config.yaml")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    llm_config = config.get('llm', {})
    if not llm_config:
        raise KeyError("配置文件中缺少 'llm' 配置")
    
    model = llm_config.get('model')
    api_key = llm_config.get('openai_api_key')
    
    if not model:
        raise KeyError("配置文件中缺少 'llm.model' 配置")
    if not api_key:
        raise KeyError("配置文件中缺少 'llm.openai_api_key' 配置")
    
    return {
        "model": model,
        "api_key": api_key
    }


async def generate_script_with_llm(description: str) -> Dict[str, Any]:
    """
    使用 LLM 根据描述生成剧本
    
    Args:
        description: 用户输入的描述文本
        
    Returns:
        {
            "text": "生成的剧本文本",
            "prompt": {
                "system_prompt": "...",
                "user_message": "..."
            },
            "request": {
                "url": "API URL",
                "headers": {...},
                "payload": {...}
            },
            "response": {...}  # 完整的API响应JSON
        }
        
    Raises:
        Exception: LLM 调用失败时抛出异常
    """
    # 加载提示词模板
    server_dir = os.path.dirname(os.path.dirname(__file__))
    prompt_path = os.path.join(server_dir, "prompts", "generation", "script_generation.txt")
    
    try:
        template = load_prompt_template(prompt_path)
    except FileNotFoundError as e:
        raise Exception(f"无法加载提示词模板: {str(e)}")
    
    # 获取系统提示词（提示词文件已经是完整的系统提示词）
    system_prompt = template.strip()
    
    # 加载 LLM 配置
    try:
        llm_config = load_llm_config()
    except (FileNotFoundError, KeyError) as e:
        raise Exception(f"无法加载 LLM 配置: {str(e)}")
    
    # 构建消息：系统提示词 + 用户输入
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": description
        }
    ]
    
    # 调用 LLM
    try:
        # 添加 server 目录到 Python 路径，以便导入 utils 包
        import sys
        if server_dir not in sys.path:
            sys.path.insert(0, server_dir)
        
        # 直接调用 query_openrouter，避免 query_llm.py 中的配置加载问题
        import requests
        import json
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {llm_config['api_key']}",
            "HTTP-Referer": "https://comicmaker.app",
            "X-Title": "ComicMaker"
        }
        
        payload = {
            "model": llm_config["model"],
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.7
        }
        
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        
        data = resp.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            script = data["choices"][0]["message"]["content"]
            if not script:
                raise Exception("LLM 返回的内容为空")
            
            # 提取提示词信息
            prompt_info = {
                "system_prompt": system_prompt,
                "user_message": description
            }
            
            # 处理请求参数（简化，避免包含敏感信息）
            request_payload = payload.copy()
            
            # 返回剧本、提示词、请求参数和响应JSON
            return {
                "text": script,
                "prompt": prompt_info,
                "request": {
                    "url": url,
                    "headers": {k: v if k != "Authorization" else "Bearer ***" for k, v in headers.items()},
                    "payload": request_payload
                },
                "response": data
            }
        else:
            raise Exception("LLM 返回格式无效")
        
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                raise Exception(f"OpenRouter API 错误: {error_data}")
            except json.JSONDecodeError:
                raise Exception(f"HTTP 错误: {e.response.status_code}, {e.response.text}")
        raise Exception(f"LLM 调用失败: {str(e)}")
    except Exception as e:
        raise Exception(f"LLM 调用失败: {str(e)}")


async def generate_description_with_llm(
    image_path: str,
    material_type: str,
    user_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用 LLM 根据图片和描述生成详细描述设定
    
    Args:
        image_path: 图片文件路径
        material_type: 素材类型（"人物"、"场景"、"道具"）
        user_description: 用户提供的额外描述（可选）
        
    Returns:
        {
            "description": "生成的描述文本",
            "request": {
                "url": "API URL",
                "headers": {...},
                "payload": {...}
            },
            "response": {...}  # 完整的API响应JSON
        }
        
    Raises:
        Exception: LLM 调用失败时抛出异常
    """
    # 检查图片文件是否存在
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    # 加载提示词模板
    server_dir = os.path.dirname(os.path.dirname(__file__))
    prompt_path = os.path.join(server_dir, "prompts", "generation", "image_to_description.txt")
    
    try:
        template = load_prompt_template(prompt_path)
    except FileNotFoundError as e:
        raise Exception(f"无法加载提示词模板: {str(e)}")
    
    # 替换模板中的变量
    user_desc_text = user_description if user_description else ""
    system_prompt = replace_prompt_variables(
        template,
        material_type=material_type,
        user_description=user_desc_text
    ).strip()
    
    # 加载 LLM 配置
    try:
        llm_config = load_llm_config()
    except (FileNotFoundError, KeyError) as e:
        raise Exception(f"无法加载 LLM 配置: {str(e)}")
    
    # 导入图片编码和多模态消息构建函数
    import sys
    if server_dir not in sys.path:
        sys.path.insert(0, server_dir)
    
    from utils.query_llm import _encode_image_to_base64, prepare_multimodal_messages_openai_format
    
    # 编码图片
    try:
        base64_image = _encode_image_to_base64(image_path)
    except Exception as e:
        raise Exception(f"图片编码失败: {str(e)}")
    
    # 构建用户消息文本，明确携带类型信息
    user_message_text = f"请分析这张图片并生成描述设定。\n\n类型：{material_type}"
    if user_description:
        user_message_text += f"\n\n用户提供的额外描述：{user_description}"
    
    # 构建多模态消息
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    
    # 使用 prepare_multimodal_messages_openai_format 构建用户消息
    user_messages = prepare_multimodal_messages_openai_format(
        prompt_text=user_message_text,
        image_paths=[image_path],
        existing_messages=[]
    )
    messages.extend(user_messages)
    
    # 调用 OpenRouter API
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {llm_config['api_key']}",
            "HTTP-Referer": "https://comicmaker.app",
            "X-Title": "ComicMaker"
        }
        
        payload = {
            "model": llm_config["model"],
            "messages": messages,
            "max_tokens": 200,  # 限制在100字以内，200 tokens足够
            "temperature": 0.7
        }
        
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        
        data = resp.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            description = data["choices"][0]["message"]["content"]
            if not description:
                raise Exception("LLM 返回的内容为空")
            
            # 不再截断，让AI自己控制字数（通过提示词限制）
            description = description.strip()
            
            # 处理请求参数，简化图片数据（base64太长）
            request_payload = payload.copy()
            if "messages" in request_payload:
                # 简化消息中的图片数据
                simplified_messages = []
                for msg in request_payload["messages"]:
                    simplified_msg = msg.copy()
                    if isinstance(msg.get("content"), list):
                        simplified_content = []
                        for item in msg["content"]:
                            if item.get("type") == "image_url":
                                # 只显示图片URL的前100个字符
                                url_data = item.get("image_url", {}).get("url", "")
                                if len(url_data) > 100:
                                    simplified_content.append({
                                        "type": "image_url",
                                        "image_url": {
                                            "url": url_data[:100] + "... (base64数据已截断，实际长度: " + str(len(url_data)) + " 字符)"
                                        }
                                    })
                                else:
                                    simplified_content.append(item)
                            else:
                                simplified_content.append(item)
                        simplified_msg["content"] = simplified_content
                    simplified_messages.append(simplified_msg)
                request_payload["messages"] = simplified_messages
            
            # 提取提示词信息（system prompt 和 user message）
            prompt_info = {
                "system_prompt": system_prompt,
                "user_message": user_message_text
            }
            
            # 返回描述、提示词、请求参数和响应JSON
            return {
                "description": description,
                "prompt": prompt_info,  # 单独保存提示词信息
                "request": {
                    "url": url,
                    "headers": {k: v if k != "Authorization" else "Bearer ***" for k, v in headers.items()},  # 隐藏API Key
                    "payload": request_payload
                },
                "response": data  # 完整的API响应JSON
            }
        else:
            raise Exception("LLM 返回格式无效")
        
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                raise Exception(f"OpenRouter API 错误: {error_data}")
            except json.JSONDecodeError:
                raise Exception(f"HTTP 错误: {e.response.status_code}, {e.response.text}")
        raise Exception(f"LLM 调用失败: {str(e)}")
    except Exception as e:
        raise Exception(f"LLM 调用失败: {str(e)}")


async def generate_style_description_with_llm(
    image_path: str,
    user_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用 LLM 根据图片和描述生成风格描述设定
    
    Args:
        image_path: 图片文件路径
        user_description: 用户提供的额外描述（可选）
        
    Returns:
        {
            "style_description": "生成的风格描述文本",
            "request": {
                "url": "API URL",
                "headers": {...},
                "payload": {...}
            },
            "response": {...}  # 完整的API响应JSON
        }
        
    Raises:
        Exception: LLM 调用失败时抛出异常
    """
    # 检查图片文件是否存在
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    # 加载提示词模板
    server_dir = os.path.dirname(os.path.dirname(__file__))
    prompt_path = os.path.join(server_dir, "prompts", "generation", "image_to_style_description.txt")
    
    try:
        template = load_prompt_template(prompt_path)
    except FileNotFoundError as e:
        raise Exception(f"无法加载提示词模板: {str(e)}")
    
    # 替换模板中的变量
    user_desc_text = user_description if user_description else ""
    system_prompt = replace_prompt_variables(
        template,
        user_description=user_desc_text
    ).strip()
    
    # 加载 LLM 配置
    try:
        llm_config = load_llm_config()
    except (FileNotFoundError, KeyError) as e:
        raise Exception(f"无法加载 LLM 配置: {str(e)}")
    
    # 导入图片编码和多模态消息构建函数
    import sys
    if server_dir not in sys.path:
        sys.path.insert(0, server_dir)
    
    from utils.query_llm import _encode_image_to_base64, prepare_multimodal_messages_openai_format
    
    # 编码图片
    try:
        base64_image = _encode_image_to_base64(image_path)
    except Exception as e:
        raise Exception(f"图片编码失败: {str(e)}")
    
    # 构建用户消息文本
    user_message_text = "请分析这张图片并生成风格描述。"
    if user_description:
        user_message_text += f"\n\n用户提供的额外描述：{user_description}"
    
    # 构建多模态消息
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    
    # 使用 prepare_multimodal_messages_openai_format 构建用户消息
    user_messages = prepare_multimodal_messages_openai_format(
        prompt_text=user_message_text,
        image_paths=[image_path],
        existing_messages=[]
    )
    messages.extend(user_messages)
    
    # 调用 OpenRouter API
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {llm_config['api_key']}",
            "HTTP-Referer": "https://comicmaker.app",
            "X-Title": "ComicMaker"
        }
        
        payload = {
            "model": llm_config["model"],
            "messages": messages,
            "max_tokens": 200,  # 限制在100字以内，200 tokens足够
            "temperature": 0.7
        }
        
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        
        data = resp.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            style_description = data["choices"][0]["message"]["content"]
            if not style_description:
                raise Exception("LLM 返回的内容为空")
            
            style_description = style_description.strip()
            
            # 处理请求参数，简化图片数据（base64太长）
            request_payload = payload.copy()
            if "messages" in request_payload:
                # 简化消息中的图片数据
                simplified_messages = []
                for msg in request_payload["messages"]:
                    simplified_msg = msg.copy()
                    if isinstance(msg.get("content"), list):
                        simplified_content = []
                        for item in msg["content"]:
                            if item.get("type") == "image_url":
                                # 只显示图片URL的前100个字符
                                url_data = item.get("image_url", {}).get("url", "")
                                if len(url_data) > 100:
                                    simplified_content.append({
                                        "type": "image_url",
                                        "image_url": {
                                            "url": url_data[:100] + "... (base64数据已截断，实际长度: " + str(len(url_data)) + " 字符)"
                                        }
                                    })
                                else:
                                    simplified_content.append(item)
                            else:
                                simplified_content.append(item)
                        simplified_msg["content"] = simplified_content
                    simplified_messages.append(simplified_msg)
                request_payload["messages"] = simplified_messages
            
            # 提取提示词信息（system prompt 和 user message）
            prompt_info = {
                "system_prompt": system_prompt,
                "user_message": user_message_text
            }
            
            return {
                "style_description": style_description,
                "prompt": prompt_info,  # 单独保存提示词信息
                "request": {
                    "url": url,
                    "headers": {k: v if k != "Authorization" else "Bearer ***" for k, v in headers.items()},  # 隐藏API Key
                    "payload": request_payload
                },
                "response": data  # 完整的API响应JSON
            }
        else:
            raise Exception("LLM 返回格式无效")
        
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                raise Exception(f"OpenRouter API 错误: {error_data}")
            except json.JSONDecodeError:
                raise Exception(f"HTTP 错误: {e.response.status_code}, {e.response.text}")
        raise Exception(f"LLM 调用失败: {str(e)}")
    except Exception as e:
        raise Exception(f"LLM 调用失败: {str(e)}")


async def generate_text_to_image(
    prompt: str,
    model: str,
    aspect_ratio: str,
    resolution: str,
    material_type: str = None
) -> Dict[str, Any]:
    """
    使用真实 API 生成图片
    
    Args:
        prompt: 图片生成提示词
        model: 模型名称（seedream4.5, wan2.6, nanopro）
        aspect_ratio: 比例（1:1, 3:4, 4:3, 16:9, 9:16）
        resolution: 分辨率（1k, 2k）
        material_type: 类型（人物/场景/道具，可选）
    
    Returns:
        dict: 包含 success, output_path, url, error 的字典
    """
    # 加载配置
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    api_key = config.get("image_gen", {}).get("wavespeed_api")
    if not api_key:
        api_key = config.get("video_gen", {}).get("wavespeed_api")
    
    if not api_key:
        raise Exception("未找到 Wavespeed API 密钥配置")
    
    # 准备输出目录
    output_id = generate_id()
    output_dir = get_output_path(ToolType.TEXT_TO_IMAGE.value, output_id)
    ensure_dir(output_dir)
    image_path = os.path.join(output_dir, "image.jpg")
    
    # 根据模型类型调用不同的 API
    try:
        if model == "seedream4.5":
            # 计算尺寸
            size = calculate_image_size(aspect_ratio, resolution)
            result = await asyncio.to_thread(
                seedream_v4_5_text_to_image,
                api_key, prompt, size, image_path
            )
        elif model == "wan2.6":
            # 计算尺寸（wan2.6 使用单独的计算函数，限制在 768-1440 范围内）
            from utils.wavespeed_api import calculate_image_size_wan26
            size = calculate_image_size_wan26(aspect_ratio, resolution)
            result = await asyncio.to_thread(
                wan_2_6_text_to_image,
                api_key, prompt, size, image_path
            )
        elif model == "nanopro":
            result = await asyncio.to_thread(
                nano_banana_pro_text_to_image,
                api_key, prompt, aspect_ratio, resolution, image_path
            )
        else:
            raise ValueError(f"不支持的模型: {model}")
        
        if not result.get('success'):
            raise Exception(result.get('error', '图片生成失败'))
        
        # 如果返回的是 URL，需要下载
        output_url = result.get('url') or result.get('output_path')
        if output_url and output_url.startswith('http'):
            download_image(output_url, image_path)
        
        # 构建 API 请求信息（根据模型类型）
        api_request = {}
        api_response = {}
        
        if model == "seedream4.5":
            size = calculate_image_size(aspect_ratio, resolution)
            api_request = {
                "url": "https://api.wavespeed.ai/api/v3/bytedance/seedream-v4.5",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer ***"
                },
                "payload": {
                    "prompt": prompt,
                    "size": size,
                    "seed": int(datetime.now().timestamp())
                }
            }
        elif model == "wan2.6":
            from utils.wavespeed_api import calculate_image_size_wan26
            size = calculate_image_size_wan26(aspect_ratio, resolution)
            api_request = {
                "url": "https://api.wavespeed.ai/api/v3/alibaba/wan-2.6/text-to-image",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer ***"
                },
                "payload": {
                    "prompt": prompt,
                    "size": size,
                    "seed": int(datetime.now().timestamp())
                }
            }
        elif model == "nanopro":
            api_request = {
                "url": "https://api.wavespeed.ai/api/v3/google/nano-banana-pro/text-to-image",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer ***"
                },
                "payload": {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "resolution": resolution,
                    "seed": int(datetime.now().timestamp())
                }
            }
        
        # 从结果中提取响应信息（如果有）
        api_response = result.get('response_data', {})
        
        return {
            'success': True,
            'output_path': image_path,
            'url': f"/data/tools/outputs/{ToolType.TEXT_TO_IMAGE.value}/{output_id}/image.jpg",
            'api_request': api_request,
            'api_response': api_response
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


async def generate_image_to_image(
    prompt: str,
    image_paths: List[str],
    model: str,
    aspect_ratio: str,
    resolution: str
) -> Dict[str, Any]:
    """
    使用真实 API 进行图生图
    
    Args:
        prompt: 图片生成提示词
        image_paths: 参考图片本地路径列表（按顺序）
        model: 模型名称（seedream4.5, wan2.6, nanopro）
        aspect_ratio: 比例（1:1, 3:4, 4:3, 16:9, 9:16）
        resolution: 分辨率（1k, 2k）
    
    Returns:
        dict: 包含 success, output_path, url, error 的字典
    """
    # 加载配置
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    api_key = config.get("image_gen", {}).get("wavespeed_api")
    if not api_key:
        api_key = config.get("video_gen", {}).get("wavespeed_api")
    
    if not api_key:
        raise Exception("未找到 Wavespeed API 密钥配置")
    
    # 在调用 API 前，先将所有图片上传到 OSS，获取 URL
    from utils.oss_upload import upload_image_to_oss_with_config
    
    image_urls = []
    for idx, img_path in enumerate(image_paths):
        try:
            oss_result = upload_image_to_oss_with_config(local_image_path=img_path)
            if oss_result.get("success"):
                image_urls.append(oss_result["url"])
                logger.info(f"图片 {idx} 上传到 OSS 成功: {oss_result['url']}")
            else:
                raise Exception(f"图片 {idx} 上传到 OSS 失败: {oss_result.get('error', '未知错误')}")
        except Exception as e:
            logger.error(f"上传图片到 OSS 失败: {str(e)}")
            raise Exception(f"上传图片到 OSS 失败: {str(e)}")
    
    # 准备输出目录
    output_id = generate_id()
    output_dir = get_output_path(ToolType.IMAGE_TO_IMAGE.value, output_id)
    ensure_dir(output_dir)
    image_path = os.path.join(output_dir, "image.jpg")
    
    # 根据模型类型调用不同的封装函数，传入 OSS URL
    try:
        if model == "seedream4.5":
            result = await asyncio.to_thread(
                generate_image_to_image_seedream,
                api_key, prompt, image_urls, aspect_ratio, resolution, image_path
            )
        elif model == "wan2.6":
            result = await asyncio.to_thread(
                generate_image_to_image_wan26,
                api_key, prompt, image_urls, aspect_ratio, resolution, image_path
            )
        elif model == "nanopro":
            result = await asyncio.to_thread(
                generate_image_to_image_nanopro,
                api_key, prompt, image_urls, aspect_ratio, resolution, image_path
            )
        else:
            raise ValueError(f"不支持的模型: {model}")
        
        if not result.get('success'):
            raise Exception(result.get('error', '图片生成失败'))
        
        # 如果返回的是 URL，需要下载
        output_url = result.get('url') or result.get('output_path')
        if output_url and output_url.startswith('http'):
            download_image(output_url, image_path)
        
        return {
            'success': True,
            'output_path': image_path,
            'url': f"/data/tools/outputs/{ToolType.IMAGE_TO_IMAGE.value}/{output_id}/image.jpg",
            'api_request': result.get('api_request', {}),
            'api_response': result.get('api_response', {})
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# 任务执行函数
async def execute_task(task_id: str, tool_type: str, input_data: Dict[str, Any]):
    """执行任务"""
    try:
        if tool_type == ToolType.GENERATE_SCRIPT.value:
            description = input_data.get("description", "")
            if not description or not description.strip():
                raise ValueError("描述文本不能为空")
            result = await generate_script_with_llm(description)
            # 立即保存 API 请求信息到任务状态（用于正在处理时查看）
            api_request = result.get("request", {})
            prompt_info = result.get("prompt", {})
            prompt_text = prompt_info.get("user_message", description) if isinstance(prompt_info, dict) else description
            update_task_status(task_id, TaskStatus.PENDING, api_request=api_request, prompt=prompt_text)
            # 保存文本、提示词、请求参数和响应JSON
            output = {
                "text": result["text"],
                "raw_content": result["text"],  # 原始内容（与text相同）
                "prompt": prompt_info,  # 提示词信息
                "api_request": api_request,  # AI接口的请求参数
                "api_response": result.get("response", {})  # AI接口的完整响应JSON
            }
            
        elif tool_type == ToolType.GENERATE_SINGLE_SHOT_STORYBOARD.value:
            script = input_data.get("script", "")
            expected_duration = int(input_data.get("expected_duration", 60))
            shot_duration = int(input_data.get("shot_duration", 5))
            character_materials = input_data.get("character_materials", [])
            scene_materials = input_data.get("scene_materials", [])
            prop_materials = input_data.get("prop_materials", [])
            
            if not script or not script.strip():
                raise ValueError("剧本内容不能为空")
            
            # 导入并调用LLM生成单镜头分镜脚本
            from api.content import call_llm_generate_single_shot_storyboard
            result = await call_llm_generate_single_shot_storyboard(
                script=script,
                expected_duration=expected_duration,
                shot_duration=shot_duration,
                character_materials=character_materials,
                scene_materials=scene_materials,
                prop_materials=prop_materials
            )
            
            # 立即保存 API 请求信息到任务状态（用于正在处理时查看）
            api_request = result.get("api_request", {})
            prompt_info = result.get("prompt", {})
            prompt_text = prompt_info.get("user_message", "") if isinstance(prompt_info, dict) else ""
            update_task_status(task_id, TaskStatus.PENDING, api_request=api_request, prompt=prompt_text)
            
            output = {
                "text": result.get("text", ""),
                "raw_content": result.get("text", ""),
                "prompt": prompt_info,
                "api_request": api_request,
                "api_response": result.get("api_response", {})
            }
            
        elif tool_type == ToolType.GENERATE_SHOT_PROMPTS.value:
            shot_description = input_data.get("shot_description", "")
            duration = int(input_data.get("duration", 5))
            related_materials = input_data.get("related_materials", [])
            previous_shots = input_data.get("previous_shots", [])
            next_shots = input_data.get("next_shots", [])
            
            if not shot_description or not shot_description.strip():
                raise ValueError("分镜描述不能为空")
            
            # 确保 previous_shots 和 next_shots 是列表
            if isinstance(previous_shots, str):
                import json
                try:
                    previous_shots = json.loads(previous_shots)
                except:
                    previous_shots = []
            if isinstance(next_shots, str):
                import json
                try:
                    next_shots = json.loads(next_shots)
                except:
                    next_shots = []
            
            # 导入并调用LLM生成分镜提示词
            from api.content import call_llm_generate_shot_prompts
            result = await call_llm_generate_shot_prompts(
                related_materials=related_materials,
                shot_description=shot_description,
                duration=duration,
                previous_shots=previous_shots,
                next_shots=next_shots
            )
            
            # 立即保存 API 请求信息到任务状态（用于正在处理时查看）
            api_request = result.get("api_request", {})
            prompt_info = result.get("prompt", {})
            prompt_text = prompt_info.get("user_message", "") if isinstance(prompt_info, dict) else ""
            update_task_status(task_id, TaskStatus.PENDING, api_request=api_request, prompt=prompt_text)
            
            output = {
                "text": result.get("text", ""),
                "raw_content": result.get("text", ""),
                "prompt": prompt_info,
                "api_request": api_request,
                "api_response": result.get("api_response", {})
            }
            
        elif tool_type == ToolType.GENERATE_STORYBOARD.value:
            script = input_data.get("script", "")
            # 导入并调用LLM生成分镜脚本
            from api.content import call_llm_generate_storyboard
            result = await call_llm_generate_storyboard(script)
            # TODO: 当实现真实LLM调用时，需要保存提示词、请求参数和响应JSON
            output = {
                "text": result,
                "raw_content": result,
                "prompt": {
                    "system_prompt": "分镜脚本生成（待实现真实LLM调用）",
                    "user_message": script
                },
                "api_request": {},
                "api_response": {}
            }
            
        elif tool_type == ToolType.IMAGE_TO_DESCRIPTION.value:
            image_path = input_data.get("image_path", "")
            material_type = input_data.get("material_type", "")
            user_description = input_data.get("description", None)  # 可选的用户描述
            if not image_path or not material_type:
                raise ValueError("image_path 和 material_type 参数必需")
            result = await generate_description_with_llm(image_path, material_type, user_description)
            # 立即保存 API 请求信息到任务状态（用于正在处理时查看）
            api_request = result.get("request", {})
            prompt_info = result.get("prompt", {})
            prompt_text = prompt_info.get("user_message", "") if isinstance(prompt_info, dict) else ""
            update_task_status(task_id, TaskStatus.PENDING, api_request=api_request, prompt=prompt_text)
            # 保存描述、提示词、请求参数和响应JSON
            output = {
                "description": result["description"],  # 处理后的描述（用于显示）
                "raw_content": result["description"],  # AI返回的完整原始内容（与description相同，因为不再截断）
                "prompt": prompt_info,  # 提示词信息（system prompt 和 user message）
                "api_request": api_request,  # AI接口的请求参数
                "api_response": result.get("response", {})  # AI接口的完整响应JSON
            }
            
        elif tool_type == ToolType.IMAGE_TO_STYLE_DESCRIPTION.value:
            image_path = input_data.get("image_path", "")
            user_description = input_data.get("description", None)  # 可选的用户描述
            if not image_path:
                raise ValueError("image_path 参数必需")
            result = await generate_style_description_with_llm(image_path, user_description)
            # 立即保存 API 请求信息到任务状态（用于正在处理时查看）
            api_request = result.get("request", {})
            prompt_info = result.get("prompt", {})
            prompt_text = prompt_info.get("user_message", "") if isinstance(prompt_info, dict) else ""
            update_task_status(task_id, TaskStatus.PENDING, api_request=api_request, prompt=prompt_text)
            # 保存风格描述、提示词、请求参数和响应JSON
            output = {
                "style_description": result["style_description"],  # 处理后的风格描述（用于显示）
                "raw_content": result["style_description"],  # AI返回的完整原始内容
                "prompt": prompt_info,  # 提示词信息（system prompt 和 user message）
                "api_request": api_request,  # AI接口的请求参数
                "api_response": result.get("response", {})  # AI接口的完整响应JSON
            }
            
        elif tool_type == ToolType.TEXT_TO_IMAGE.value:
            prompt = input_data.get("prompt", "")
            material_type = input_data.get("material_type", "")
            model = input_data.get("model", "seedream4.5")
            aspect_ratio = input_data.get("aspect_ratio", "16:9")
            resolution = input_data.get("resolution", "1k")
            result = await generate_text_to_image(prompt, model, aspect_ratio, resolution, material_type)
            if not result.get('success'):
                raise Exception(result.get('error', '图片生成失败'))
            # 立即保存 API 请求信息到任务状态（用于正在处理时查看）
            api_request = result.get('api_request', {})
            update_task_status(task_id, TaskStatus.PENDING, api_request=api_request, prompt=prompt)
            output = {
                "image_path": result.get('output_path'),
                "url": result.get('url'),
                "prompt": {
                    "user_message": prompt  # 文生图的提示词就是用户输入的 prompt
                },
                "api_request": api_request,
                "api_response": result.get('api_response', {})
            }
            
        elif tool_type == ToolType.IMAGE_TO_IMAGE.value:
            prompt = input_data.get("prompt", "")
            image_paths = input_data.get("image_paths", [])
            model = input_data.get("model", "seedream4.5")
            aspect_ratio = input_data.get("aspect_ratio", "16:9")
            resolution = input_data.get("resolution", "1k")
            if not image_paths:
                raise ValueError("image_paths 参数必需且不能为空")
            # generate_image_to_image 会在内部将图片上传到 OSS 并获取 URL
            result = await generate_image_to_image(prompt, image_paths, model, aspect_ratio, resolution)
            if not result.get('success'):
                raise Exception(result.get('error', '图片生成失败'))
            # 立即保存 API 请求信息到任务状态（用于正在处理时查看）
            api_request = result.get('api_request', {})
            update_task_status(task_id, TaskStatus.PENDING, api_request=api_request, prompt=prompt)
            output = {
                "image_path": result.get('output_path'),
                "url": result.get('url'),
                "prompt": {
                    "user_message": prompt  # 图生图的提示词就是用户输入的 prompt
                },
                "api_request": api_request,
                "api_response": result.get('api_response', {})
            }
            
        elif tool_type == ToolType.VIDU_REF_IMAGE_TO_VIDEO.value:
            # vidu 参考生视频
            prompt = input_data.get("prompt", "")
            image_paths = input_data.get("image_paths", [])
            aspect_ratio = input_data.get("aspect_ratio", "16:9")
            resolution = input_data.get("resolution", "720p")
            duration = input_data.get("duration", 5)
            
            if not prompt or not image_paths:
                raise ValueError("prompt 和 image_paths 参数必需")
            
            # 加载配置
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            api_key = config.get("video_gen", {}).get("wavespeed_api")
            if not api_key:
                api_key = config.get("image_gen", {}).get("wavespeed_api")
            
            if not api_key:
                raise Exception("未找到 Wavespeed API 密钥配置")
            
            # 上传图片到 OSS，获取 URL 列表
            from utils.oss_upload import upload_image_to_oss_with_config
            
            image_urls = []
            for idx, img_path in enumerate(image_paths):
                try:
                    oss_result = upload_image_to_oss_with_config(local_image_path=img_path)
                    if oss_result.get("success"):
                        image_urls.append(oss_result["url"])
                        logger.info(f"图片 {idx} 上传到 OSS 成功: {oss_result['url']}")
                    else:
                        raise Exception(f"图片 {idx} 上传到 OSS 失败: {oss_result.get('error', '未知错误')}")
                except Exception as e:
                    logger.error(f"上传图片到 OSS 失败: {str(e)}")
                    raise Exception(f"上传图片到 OSS 失败: {str(e)}")
            
            # 调用 vidu API
            result = vidu_reference_to_video_q2(
                api_key=api_key,
                prompt=prompt,
                image_urls=image_urls,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                duration=duration
            )
            
            if not result.get('success'):
                raise Exception(result.get('error', '视频生成失败'))
            
            # 下载视频到本地
            output_url = result.get('output_url')
            video_url = output_url
            if output_url and output_url.startswith('http'):
                # 生成输出目录和文件名
                output_id = generate_id()
                output_dir = get_output_path(ToolType.VIDU_REF_IMAGE_TO_VIDEO.value, output_id)
                ensure_dir(output_dir)
                video_path = os.path.join(output_dir, "video.mp4")
                
                # 下载视频
                download_result = download_video(output_url, video_path)
                if download_result.get('success'):
                    video_url = f"/data/tools/outputs/{ToolType.VIDU_REF_IMAGE_TO_VIDEO.value}/{output_id}/video.mp4"
                    logger.info(f"视频下载成功: {output_url} -> {video_url}")
                else:
                    logger.warning(f"视频下载失败，使用原始URL: {output_url}, 错误: {download_result.get('error')}")
            
            output = {
                "video_url": video_url,
                "api_request": result.get('api_request', {}),
                "api_response": result.get('api_response', {})
            }
            
        elif tool_type == ToolType.SORA_IMAGE_TO_VIDEO.value:
            # sora 生视频
            prompt = input_data.get("prompt", "")
            image_path = input_data.get("image_path", "")
            duration = input_data.get("duration", 4)
            
            if not prompt or not image_path:
                raise ValueError("prompt 和 image_path 参数必需")
            
            # 加载配置
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            api_key = config.get("video_gen", {}).get("wavespeed_api")
            if not api_key:
                api_key = config.get("image_gen", {}).get("wavespeed_api")
            
            if not api_key:
                raise Exception("未找到 Wavespeed API 密钥配置")
            
            # 上传图片到 OSS，获取 URL
            from utils.oss_upload import upload_image_to_oss_with_config
            
            try:
                oss_result = upload_image_to_oss_with_config(local_image_path=image_path)
                if not oss_result.get("success"):
                    raise Exception(f"图片上传到 OSS 失败: {oss_result.get('error', '未知错误')}")
                image_url = oss_result["url"]
                logger.info(f"图片上传到 OSS 成功: {image_url}")
            except Exception as e:
                logger.error(f"上传图片到 OSS 失败: {str(e)}")
                raise Exception(f"上传图片到 OSS 失败: {str(e)}")
            
            # 调用 sora API
            result = sora_2_image_to_video(
                api_key=api_key,
                prompt=prompt,
                image_url=image_url,
                duration=duration
            )
            
            if not result.get('success'):
                raise Exception(result.get('error', '视频生成失败'))
            
            # 下载视频到本地
            output_url = result.get('output_url')
            video_url = output_url
            if output_url and output_url.startswith('http'):
                # 生成输出目录和文件名
                output_id = generate_id()
                output_dir = get_output_path(ToolType.SORA_IMAGE_TO_VIDEO.value, output_id)
                ensure_dir(output_dir)
                video_path = os.path.join(output_dir, "video.mp4")
                
                # 下载视频
                download_result = download_video(output_url, video_path)
                if download_result.get('success'):
                    video_url = f"/data/tools/outputs/{ToolType.SORA_IMAGE_TO_VIDEO.value}/{output_id}/video.mp4"
                    logger.info(f"视频下载成功: {output_url} -> {video_url}")
                else:
                    logger.warning(f"视频下载失败，使用原始URL: {output_url}, 错误: {download_result.get('error')}")
            
            output = {
                "video_url": video_url,
                "api_request": result.get('api_request', {}),
                "api_response": result.get('api_response', {})
            }
            
        elif tool_type == ToolType.WAN_IMAGE_TO_VIDEO.value:
            # wan 图生视频
            prompt = input_data.get("prompt", "")
            image_path = input_data.get("image_path", "")
            model = input_data.get("model", "wan2.6")
            resolution = input_data.get("resolution", "720p")
            duration = input_data.get("duration", 5)
            enable_audio = input_data.get("enable_audio", False)
            
            if not prompt or not image_path:
                raise ValueError("prompt 和 image_path 参数必需")
            
            # 加载配置
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            api_key = config.get("video_gen", {}).get("wavespeed_api")
            if not api_key:
                api_key = config.get("image_gen", {}).get("wavespeed_api")
            
            if not api_key:
                raise Exception("未找到 Wavespeed API 密钥配置")
            
            # 上传图片到 OSS，获取 URL
            from utils.oss_upload import upload_image_to_oss_with_config
            
            try:
                oss_result = upload_image_to_oss_with_config(local_image_path=image_path)
                if not oss_result.get("success"):
                    raise Exception(f"图片上传到 OSS 失败: {oss_result.get('error', '未知错误')}")
                image_url = oss_result["url"]
                logger.info(f"图片上传到 OSS 成功: {image_url}")
            except Exception as e:
                logger.error(f"上传图片到 OSS 失败: {str(e)}")
                raise Exception(f"上传图片到 OSS 失败: {str(e)}")
            
            # 根据模型版本调用不同的 API
            if model == "wan2.5":
                result = wan_2_5_image_to_video(
                    api_key=api_key,
                    prompt=prompt,
                    image_url=image_url,
                    resolution=resolution,
                    duration=duration,
                    enable_prompt_expansion=False
                )
            else:  # wan2.6
                shot_type = input_data.get("shot_type", "single")
                result = wan_2_6_image_to_video(
                    api_key=api_key,
                    prompt=prompt,
                    image_url=image_url,
                    resolution=resolution,
                    duration=duration,
                    shot_type=shot_type,
                    enable_audio=enable_audio
                )
            
            if not result.get('success'):
                raise Exception(result.get('error', '视频生成失败'))
            
            # 下载视频到本地
            output_url = result.get('output_url')
            video_url = output_url
            if output_url and output_url.startswith('http'):
                # 生成输出目录和文件名
                output_id = generate_id()
                output_dir = get_output_path(ToolType.WAN_IMAGE_TO_VIDEO.value, output_id)
                ensure_dir(output_dir)
                video_path = os.path.join(output_dir, "video.mp4")
                
                # 下载视频
                download_result = download_video(output_url, video_path)
                if download_result.get('success'):
                    video_url = f"/data/tools/outputs/{ToolType.WAN_IMAGE_TO_VIDEO.value}/{output_id}/video.mp4"
                    logger.info(f"视频下载成功: {output_url} -> {video_url}")
                else:
                    logger.warning(f"视频下载失败，使用原始URL: {output_url}, 错误: {download_result.get('error')}")
            
            output = {
                "video_url": video_url,
                "api_request": result.get('api_request', {}),
                "api_response": result.get('api_response', {})
            }
            
        elif tool_type == ToolType.KEYFRAME_TO_VIDEO.value:
            # TODO: 实现首尾帧生视频功能
            raise NotImplementedError("首尾帧生视频功能尚未实现")
            
        elif tool_type == ToolType.TEXT_TO_AUDIO.value:
            # TODO: 实现生音频功能
            raise NotImplementedError("生音频功能尚未实现")
            
        else:
            raise ValueError(f"未知的工具类型: {tool_type}")
        
        # 更新任务状态为成功
        update_task_status(task_id, TaskStatus.SUCCESS, output=output)
        
        # 创建历史记录
        create_history_record(task_id, tool_type, input_data, output)
        
    except Exception as e:
        # 更新任务状态为失败
        update_task_status(task_id, TaskStatus.FAILED, error=str(e))


# 工具创建接口
@router.post("/{tool_type}/create")
async def create_tool_task(
    tool_type: str,
    description: Optional[str] = Form(None),
    script: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    material_type: Optional[str] = Form(None),
    aspect_ratio: Optional[str] = Form(None),
    resolution: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    duration: Optional[str] = Form(None),
    enable_audio: Optional[bool] = Form(None),
    expected_duration: Optional[str] = Form(None),
    shot_duration: Optional[str] = Form(None),
    character_materials: Optional[str] = Form(None),
    scene_materials: Optional[str] = Form(None),
    prop_materials: Optional[str] = Form(None),
    shot_description: Optional[str] = Form(None),
    related_materials: Optional[str] = Form(None),
    previous_shots: Optional[str] = Form(None),
    next_shots: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    images: List[UploadFile] = File(default=[]),
    start_frame: Optional[UploadFile] = File(None),
    end_frame: Optional[UploadFile] = File(None)
):
    """创建工具任务"""
    # 验证工具类型
    try:
        ToolType(tool_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的工具类型: {tool_type}")
    
    # 构建输入数据
    input_data = {}
    
    if tool_type == ToolType.GENERATE_SCRIPT.value:
        if not description:
            raise HTTPException(status_code=400, detail="description 参数必需")
        input_data = {"description": description}
        
    elif tool_type == ToolType.GENERATE_SINGLE_SHOT_STORYBOARD.value:
        if not script:
            raise HTTPException(status_code=400, detail="script 参数必需")
        # 解析素材列表（JSON字符串）
        import json
        char_materials_list = []
        scene_materials_list = []
        prop_materials_list = []
        if character_materials:
            try:
                char_materials_list = json.loads(character_materials)
            except:
                pass
        if scene_materials:
            try:
                scene_materials_list = json.loads(scene_materials)
            except:
                pass
        if prop_materials:
            try:
                prop_materials_list = json.loads(prop_materials)
            except:
                pass
        input_data = {
            "script": script,
            "expected_duration": int(expected_duration) if expected_duration else 60,
            "shot_duration": int(shot_duration) if shot_duration else 5,
            "character_materials": char_materials_list,
            "scene_materials": scene_materials_list,
            "prop_materials": prop_materials_list
        }
        
    elif tool_type == ToolType.GENERATE_SHOT_PROMPTS.value:
        if not shot_description:
            raise HTTPException(status_code=400, detail="shot_description 参数必需")
        
        # 解析素材列表（JSON字符串）
        import json
        related_materials_list = []
        if related_materials:
            try:
                related_materials_list = json.loads(related_materials)
            except:
                pass
        
        # 解析前后分镜描述列表（JSON字符串）
        previous_shots_list = []
        if previous_shots:
            try:
                previous_shots_list = json.loads(previous_shots)
            except:
                pass
        
        next_shots_list = []
        if next_shots:
            try:
                next_shots_list = json.loads(next_shots)
            except:
                pass
        
        # duration 从 duration 字段获取
        duration_value = int(duration) if duration else 5
        
        input_data = {
            "shot_description": shot_description,
            "duration": duration_value,
            "related_materials": related_materials_list,
            "previous_shots": previous_shots_list,
            "next_shots": next_shots_list
        }
        
    elif tool_type == ToolType.GENERATE_STORYBOARD.value:
        if not script:
            raise HTTPException(status_code=400, detail="script 参数必需")
        input_data = {"script": script}
        
    elif tool_type == ToolType.IMAGE_TO_DESCRIPTION.value:
        if not image or not material_type:
            raise HTTPException(status_code=400, detail="image 和 material_type 参数必需")
        # 保存上传的图片
        output_id = generate_id()
        output_dir = get_output_path("uploads", output_id)
        ensure_dir(output_dir)
        image_path = os.path.join(output_dir, image.filename or "image.jpg")
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        input_data = {
            "image_path": image_path,
            "material_type": material_type,
            "description": description  # 可选的用户描述
        }
        
    elif tool_type == ToolType.IMAGE_TO_STYLE_DESCRIPTION.value:
        if not image:
            raise HTTPException(status_code=400, detail="image 参数必需")
        # 保存上传的图片
        output_id = generate_id()
        output_dir = get_output_path("uploads", output_id)
        ensure_dir(output_dir)
        image_path = os.path.join(output_dir, image.filename or "image.jpg")
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        input_data = {
            "image_path": image_path,
            "description": description  # 可选的用户描述
        }
        
    elif tool_type == ToolType.TEXT_TO_IMAGE.value:
        if not prompt or not material_type:
            raise HTTPException(status_code=400, detail="prompt 和 material_type 参数必需")
        input_data = {
            "prompt": prompt,
            "material_type": material_type,
            "model": model or "seedream4.5",
            "aspect_ratio": aspect_ratio or "16:9",
            "resolution": resolution or "1k"
        }
        
    elif tool_type == ToolType.IMAGE_TO_IMAGE.value:
        if not prompt:
            raise HTTPException(status_code=400, detail="prompt 参数必需")
        # 检查 images 参数
        if not images or len(images) == 0:
            raise HTTPException(status_code=400, detail="images 参数必需且至少包含一张图片")
        # 保存上传的图片到本地（按顺序），不上传 OSS
        image_paths = []
        output_id = generate_id()
        output_dir = get_output_path("uploads", output_id)
        ensure_dir(output_dir)
        for idx, img in enumerate(images):
            img_path = os.path.join(output_dir, f"image_{idx}.jpg")
            with open(img_path, "wb") as f:
                shutil.copyfileobj(img.file, f)
            image_paths.append(img_path)
        input_data = {
            "prompt": prompt,
            "image_paths": image_paths,  # 保存本地路径，在调用 API 前上传到 OSS
            "model": model or "seedream4.5",
            "aspect_ratio": aspect_ratio or "16:9",
            "resolution": resolution or "1k"
        }
        
    elif tool_type == ToolType.VIDU_REF_IMAGE_TO_VIDEO.value:
        if not images or not prompt or not aspect_ratio or not resolution or not duration:
            raise HTTPException(status_code=400, detail="images、prompt、aspect_ratio、resolution 和 duration 参数必需")
        # 限制最多7张图片
        if len(images) > 7:
            images = images[:7]
        # 将 duration 转换为整数（前端发送的是字符串）
        try:
            duration_int = int(duration) if duration else 5
        except (ValueError, TypeError):
            duration_int = 5
        # 保存上传的图片
        image_paths = []
        output_id = generate_id()
        output_dir = get_output_path("uploads", output_id)
        ensure_dir(output_dir)
        for idx, img in enumerate(images):
            img_path = os.path.join(output_dir, f"image_{idx}.jpg")
            with open(img_path, "wb") as f:
                shutil.copyfileobj(img.file, f)
            image_paths.append(img_path)
        input_data = {
            "image_paths": image_paths,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "duration": duration_int
        }
        
    elif tool_type == ToolType.SORA_IMAGE_TO_VIDEO.value:
        if not image or not prompt or not duration:
            raise HTTPException(status_code=400, detail="image、prompt 和 duration 参数必需")
        # 将 duration 转换为整数（前端发送的是字符串）
        try:
            duration_int = int(duration) if duration else 4
        except (ValueError, TypeError):
            duration_int = 4
        # 保存上传的图片
        output_id = generate_id()
        output_dir = get_output_path("uploads", output_id)
        ensure_dir(output_dir)
        image_path = os.path.join(output_dir, image.filename or "image.jpg")
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        input_data = {
            "image_path": image_path,
            "prompt": prompt,
            "duration": duration_int
        }
        
    elif tool_type == ToolType.WAN_IMAGE_TO_VIDEO.value:
        if not image or not prompt or not resolution or not duration:
            raise HTTPException(status_code=400, detail="image、prompt、resolution 和 duration 参数必需")
        # 将 duration 转换为整数（前端发送的是字符串）
        try:
            duration_int = int(duration) if duration else 5
        except (ValueError, TypeError):
            duration_int = 5
        # 保存上传的图片
        output_id = generate_id()
        output_dir = get_output_path("uploads", output_id)
        ensure_dir(output_dir)
        image_path = os.path.join(output_dir, image.filename or "image.jpg")
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        # 处理 enable_audio 参数（从 form 中获取，可能是字符串 "true"/"false"）
        enable_audio = False
        if "enable_audio" in locals() or "enable_audio" in globals():
            enable_audio_val = locals().get("enable_audio") or globals().get("enable_audio")
            if enable_audio_val:
                enable_audio = str(enable_audio_val).lower() in ("true", "1", "yes", "on")
        input_data = {
            "image_path": image_path,
            "prompt": prompt,
            "model": model or "wan2.6",
            "resolution": resolution,
            "duration": duration_int,
            "enable_audio": enable_audio if enable_audio is not None else False
        }
        
    elif tool_type == ToolType.KEYFRAME_TO_VIDEO.value:
        if not start_frame or not end_frame or not prompt or not aspect_ratio or not duration:
            raise HTTPException(status_code=400, detail="start_frame、end_frame、prompt、aspect_ratio 和 duration 参数必需")
        # 保存上传的图片
        output_id = generate_id()
        output_dir = get_output_path("uploads", output_id)
        ensure_dir(output_dir)
        start_path = os.path.join(output_dir, "start_frame.jpg")
        end_path = os.path.join(output_dir, "end_frame.jpg")
        with open(start_path, "wb") as f:
            shutil.copyfileobj(start_frame.file, f)
        with open(end_path, "wb") as f:
            shutil.copyfileobj(end_frame.file, f)
        input_data = {
            "start_frame": start_path,
            "end_frame": end_path,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration
        }
        
    elif tool_type == ToolType.TEXT_TO_AUDIO.value:
        if not text or not duration:
            raise HTTPException(status_code=400, detail="text 和 duration 参数必需")
        input_data = {"text": text, "duration": duration}
    
    # 创建任务
    task_id = create_task(tool_type, input_data)
    
    # 异步执行任务
    asyncio.create_task(execute_task(task_id, tool_type, input_data))
    
    return {"task_id": task_id, "status": "pending"}


# 历史记录接口
@router.get("/history")
async def list_history(
    tool_type: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """获取历史记录列表"""
    history_dir = get_data_path("tools", "history")
    if not os.path.exists(history_dir):
        return {"records": [], "total": 0, "page": page, "limit": limit}
    
    # 读取所有历史记录
    records = []
    for filename in os.listdir(history_dir):
        if filename.endswith(".json"):
            record_path = os.path.join(history_dir, filename)
            record = load_json(record_path)
            if record:
                # 筛选工具类型
                if tool_type and record.get("tool_type") != tool_type:
                    continue
                records.append(record)
    
    # 按时间倒序排序
    records.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # 分页
    total = len(records)
    start = (page - 1) * limit
    end = start + limit
    paginated_records = records[start:end]
    
    return {
        "records": paginated_records,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/history/{record_id}")
async def get_history_detail(record_id: str):
    """获取历史记录详情"""
    record_path = get_history_path(record_id)
    record = load_json(record_path)
    if not record:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    return record


@router.delete("/history/{record_id}")
async def delete_history(record_id: str):
    """删除历史记录"""
    record_path = get_history_path(record_id)
    if not os.path.exists(record_path):
        raise HTTPException(status_code=404, detail="历史记录不存在")
    
    # 删除记录文件
    os.remove(record_path)
    
    return {"message": "删除成功"}


@router.get("/history/{record_id}/reuse")
async def reuse_history(record_id: str):
    """获取历史记录的输入参数（用于做同款）"""
    record_path = get_history_path(record_id)
    record = load_json(record_path)
    if not record:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    
    return {
        "tool_type": record.get("tool_type"),
        "input": record.get("input")
    }

