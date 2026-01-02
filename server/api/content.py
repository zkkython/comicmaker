#!/usr/bin/env python3
"""
内容生成 API
包括分镜生成、图片生成、视频生成、音频生成
"""

from fastapi import APIRouter, HTTPException, Form
from typing import List, Dict, Any
import os
import json
import re
from datetime import datetime

from utils import (
    get_data_path, load_json, save_json, generate_id,
    ensure_dir
)
from utils.image_process import download_video

router = APIRouter()


def get_shot_path(work_id: str, episode_id: str, shot_id: str) -> str:
    """获取分镜路径"""
    return get_data_path("works", work_id, "episodes", episode_id, "shots", shot_id)


async def call_llm_generate_storyboard(script: str) -> str:
    """
    调用LLM接口，从剧本生成分镜脚本
    目前是mock实现，返回示例格式
    
    Args:
        script: 剧本内容
        
    Returns:
        分镜脚本文本
    """
    # TODO: 实际调用LLM API
    # 示例：调用 LLM API
    # response = await llm_client.generate(
    #     prompt=f"请将以下剧本转换为分镜脚本，每个分镜包含描述：\n{script}",
    #     ...
    # )
    # return response.text
    
    # Mock返回：返回用户提供的示例格式
    mock_storyboard = """分镜1: 白天，阳光明媚的贵族花园，白色雕花秋千架上坐着艾瑞莎·薇拉，她身着紫色华服，紫色长发随秋千摆动，蓝色眼眸望着远方。突然天空传来机械轰鸣，红白配色的凤凰机甲战士展开巨大翅膀俯冲而下，落地时激起烟尘
分镜2: 白天，贵族花园中央，凤凰机甲战士落地瞬间挥剑刺向艾瑞莎·薇拉，她从秋千跃起，双手凝聚橙红色火焰魔法形成护盾，镜头环绕两人快速旋转
分镜3: 白天，贵族花园战场，艾瑞莎·薇拉释放火焰魔法与凤凰机甲战士长剑碰撞，产生爆炸火光。镜头采用快速剪辑展现三个战斗回合：火焰束对斩击、空中追击、魔法阵防御。"""
    
    return mock_storyboard


async def call_llm_generate_single_shot_storyboard(
    script: str,
    expected_duration: int,
    shot_duration: int,
    character_materials: List[str] = None,
    scene_materials: List[str] = None,
    prop_materials: List[str] = None
) -> Dict[str, Any]:
    """
    调用LLM接口，从剧本生成单镜头分镜脚本
    
    Args:
        script: 剧本内容
        expected_duration: 预期总时长（秒）
        shot_duration: 单镜头预计时长（秒）
        character_materials: 人物素材名称列表
        scene_materials: 场景素材名称列表
        prop_materials: 道具素材名称列表
        
    Returns:
        dict: 包含 text（分镜脚本文本）、prompt、api_request、api_response
    """
    from utils.query_llm import prepare_multimodal_messages_openai_format, query_openrouter
    
    # 加载提示词模板
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "generation", "single_shot_storyboard.txt")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # 准备素材列表字符串
    char_materials_str = "，".join(character_materials) if character_materials else "无"
    scene_materials_str = "，".join(scene_materials) if scene_materials else "无"
    prop_materials_str = "，".join(prop_materials) if prop_materials else "无"
    
    # 替换模板变量
    prompt = prompt_template.format(
        script=script,
        expected_duration=expected_duration,
        shot_duration=shot_duration,
        character_materials=char_materials_str,
        scene_materials=scene_materials_str,
        prop_materials=prop_materials_str
    )
    
    # 准备消息（使用多模态函数，但只传入文本）
    messages = prepare_multimodal_messages_openai_format(prompt_text=prompt)
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    llm_cfg = config.get("llm", {})
    api_key = llm_cfg.get("openai_api_key")
    model = llm_cfg.get("model", "gpt-4o")
    
    # 调用LLM
    response = query_openrouter(
        api_key=api_key,
        model=model,
        messages=messages
    )
    
    content = response.get("content", "")
    
    return {
        "text": content,
        "prompt": {
            "system_prompt": "分镜脚本生成专家",
            "user_message": prompt
        },
        "api_request": {
            "model": model,
            "messages": messages
        },
        "api_response": response
    }


async def call_llm_generate_shot_prompts(
    related_materials: List[str],
    shot_description: str,
    duration: int,
    previous_shots: List[str] = None,
    next_shots: List[str] = None
) -> Dict[str, Any]:
    """
    调用LLM接口，生成分镜提示词
    
    Args:
        related_materials: 关联素材名称列表
        shot_description: 分镜描述
        duration: 预期时长（秒）
        previous_shots: 前序分镜描述列表（最多3个，按时间倒序）
        next_shots: 后续分镜描述列表（最多3个，按时间正序）
        
    Returns:
        dict: 包含 text（提示词文本）、prompt、api_request、api_response
    """
    from utils.query_llm import prepare_multimodal_messages_openai_format, query_openrouter
    
    # 加载提示词模板
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "generation", "shot_prompts.txt")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # 准备素材列表字符串
    materials_str = "，".join(related_materials) if related_materials else "无"
    
    # 准备前序分镜描述字符串
    if previous_shots:
        previous_str = "\n".join([f"- 前序分镜{i+1}：{desc}" for i, desc in enumerate(previous_shots[:3])])
    else:
        previous_str = "无"
    
    # 准备后续分镜描述字符串
    if next_shots:
        next_str = "\n".join([f"- 后续分镜{i+1}：{desc}" for i, desc in enumerate(next_shots[:3])])
    else:
        next_str = "无"
    
    # 替换模板变量
    prompt = prompt_template.format(
        related_materials=materials_str,
        shot_description=shot_description,
        duration=duration,
        previous_shots=previous_str,
        next_shots=next_str
    )
    
    # 准备消息
    messages = prepare_multimodal_messages_openai_format(prompt_text=prompt)
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    llm_cfg = config.get("llm", {})
    api_key = llm_cfg.get("openai_api_key")
    model = llm_cfg.get("model", "gpt-4o")
    
    # 调用LLM
    response = query_openrouter(
        api_key=api_key,
        model=model,
        messages=messages
    )
    
    content = response.get("content", "")
    
    return {
        "text": content,
        "prompt": {
            "system_prompt": "分镜提示词生成专家",
            "user_message": prompt
        },
        "api_request": {
            "model": model,
            "messages": messages
        },
        "api_response": response
    }


@router.post("/{work_id}/{episode_id}/generate-storyboard")
async def generate_storyboard(
    work_id: str,
    episode_id: str,
    script: str = Form(...)
):
    """从剧本生成分镜脚本文本（调用LLM接口）"""
    episode_path = get_data_path("works", work_id, "episodes", episode_id)
    
    # 调用LLM接口生成分镜脚本
    if not script or not script.strip():
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="剧本内容不能为空")
    
    # 调用LLM生成分镜脚本
    storyboard_text = await call_llm_generate_storyboard(script)
    
    storyboard = {
        "text": storyboard_text,
        "confirmed": False
    }
    
    storyboard_path = os.path.join(episode_path, "storyboard.json")
    save_json(storyboard_path, storyboard)
    
    return storyboard


@router.post("/{work_id}/{episode_id}/{shot_id}/generate-images")
async def generate_images(
    work_id: str,
    episode_id: str,
    shot_id: str,
    prompt: str = Form(...)
):
    """生成候选图片"""
    # TODO: 调用 text-to-image API
    # 这里先返回示例数据
    shot_path = get_shot_path(work_id, episode_id, shot_id)
    images_dir = os.path.join(shot_path, "images")
    ensure_dir(images_dir)
    
    # 实际应该调用 text_to_image_generate API
    # 这里返回示例路径
    candidates = []
    for i in range(1, 4):
        candidate_path = os.path.join(images_dir, f"candidate_{i}.jpg")
        # TODO: 实际生成图片并保存
        candidates.append({
            "path": f"images/candidate_{i}.jpg",
            "url": f"/data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/images/candidate_{i}.jpg"
        })
    
    # 更新分镜元数据
    meta_path = os.path.join(shot_path, "meta.json")
    meta = load_json(meta_path) or {}
    meta["image_candidates"] = candidates
    save_json(meta_path, meta)
    
    return {"candidates": candidates}


@router.post("/{work_id}/{episode_id}/{shot_id}/select-image")
async def select_image(
    work_id: str,
    episode_id: str,
    shot_id: str,
    image_path: str = Form(...)
):
    """选择图片"""
    shot_path = get_shot_path(work_id, episode_id, shot_id)
    meta_path = os.path.join(shot_path, "meta.json")
    meta = load_json(meta_path) or {}
    
    meta["selected_image"] = image_path
    save_json(meta_path, meta)
    
    return {"message": "Image selected", "image_path": image_path}


@router.post("/{work_id}/{episode_id}/{shot_id}/generate-video")
async def generate_video(
    work_id: str,
    episode_id: str,
    shot_id: str,
    prompt: str = Form(...)
):
    """生成视频"""
    # TODO: 调用 text-to-video API
    shot_path = get_shot_path(work_id, episode_id, shot_id)
    videos_dir = os.path.join(shot_path, "videos")
    ensure_dir(videos_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    video_filename = f"video_{timestamp}.mp4"
    video_path = os.path.join(videos_dir, video_filename)
    
    # TODO: 实际生成视频并保存
    # 这里返回示例路径
    
    # 更新分镜元数据
    meta_path = os.path.join(shot_path, "meta.json")
    meta = load_json(meta_path) or {}
    meta["video"] = f"videos/{video_filename}"
    save_json(meta_path, meta)
    
    return {
        "video_path": f"videos/{video_filename}",
        "url": f"/data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/{video_filename}"
    }


@router.post("/{work_id}/{episode_id}/{shot_id}/download-video")
async def download_video_to_shot(
    work_id: str,
    episode_id: str,
    shot_id: str,
    video_url: str = Form(...)
):
    """下载视频到分镜目录"""
    from fastapi import HTTPException
    
    if not video_url or not video_url.startswith('http'):
        raise HTTPException(status_code=400, detail="无效的视频URL")
    
    shot_path = get_shot_path(work_id, episode_id, shot_id)
    videos_dir = os.path.join(shot_path, "videos")
    ensure_dir(videos_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    video_filename = f"reference_video_{timestamp}.mp4"
    video_path = os.path.join(videos_dir, video_filename)
    
    # 下载视频
    download_result = download_video(video_url, video_path)
    if not download_result.get('success'):
        raise HTTPException(status_code=500, detail=f"视频下载失败: {download_result.get('error')}")
    
    local_url = f"/data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/{video_filename}"
    
    return {
        "video_path": f"videos/{video_filename}",
        "url": local_url
    }


@router.post("/{work_id}/{episode_id}/{shot_id}/generate-audio")
async def generate_audio(
    work_id: str,
    episode_id: str,
    shot_id: str,
    prompt: str = Form(...)
):
    """生成音频"""
    # TODO: 调用 TTS API
    shot_path = get_shot_path(work_id, episode_id, shot_id)
    audio_dir = os.path.join(shot_path, "audio")
    ensure_dir(audio_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    audio_filename = f"audio_{timestamp}.mp3"
    audio_path = os.path.join(audio_dir, audio_filename)
    
    # TODO: 实际生成音频并保存
    # 这里返回示例路径
    
    # 更新分镜元数据
    meta_path = os.path.join(shot_path, "meta.json")
    meta = load_json(meta_path) or {}
    meta["audio"] = f"audio/{audio_filename}"
    save_json(meta_path, meta)
    
    return {
        "audio_path": f"audio/{audio_filename}",
        "url": f"/data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/audio/{audio_filename}"
    }


@router.get("/{work_id}/{episode_id}/{shot_id}")
async def get_shot(work_id: str, episode_id: str, shot_id: str):
    """获取分镜详情"""
    shot_path = get_shot_path(work_id, episode_id, shot_id)
    meta_path = os.path.join(shot_path, "meta.json")
    meta = load_json(meta_path) or {}
    
    meta["id"] = shot_id
    return meta


@router.put("/{work_id}/{episode_id}/{shot_id}/prompts")
async def update_prompts(
    work_id: str,
    episode_id: str,
    shot_id: str,
    image_prompt: str = Form(None),
    video_prompt: str = Form(None),
    audio_prompt: str = Form(None)
):
    """更新分镜提示词"""
    shot_path = get_shot_path(work_id, episode_id, shot_id)
    meta_path = os.path.join(shot_path, "meta.json")
    meta = load_json(meta_path) or {}
    
    if image_prompt is not None:
        meta["image_prompt"] = image_prompt
    if video_prompt is not None:
        meta["video_prompt"] = video_prompt
    if audio_prompt is not None:
        meta["audio_prompt"] = audio_prompt
    
    save_json(meta_path, meta)
    
    # 同时更新 storyboard.json 中的对应分镜数据
    episode_path = get_data_path("works", work_id, "episodes", episode_id)
    storyboard_path = os.path.join(episode_path, "storyboard.json")
    storyboard = load_json(storyboard_path) or {}
    
    if "shots" in storyboard:
        for shot in storyboard["shots"]:
            if shot.get("id") == shot_id:
                if image_prompt is not None:
                    shot["image_prompt"] = image_prompt
                if video_prompt is not None:
                    shot["video_prompt"] = video_prompt
                if audio_prompt is not None:
                    shot["audio_prompt"] = audio_prompt
                break
        save_json(storyboard_path, storyboard)
    
    meta["id"] = shot_id
    return meta


@router.put("/{work_id}/{episode_id}/{shot_id}")
async def update_shot(
    work_id: str,
    episode_id: str,
    shot_id: str,
    description: str = Form(None),
    image_prompt: str = Form(None),
    video_prompt: str = Form(None),
    audio_prompt: str = Form(None),
    duration: str = Form(None),
    reference_video_prompt: str = Form(None),
    dialogue_prompt: str = Form(None),
    video_task_id: str = Form(None),
    current_video: str = Form(None),
    video_history: str = Form(None)
):
    """更新分镜字段（描述和提示词）"""
    from fastapi import HTTPException
    
    episode_path = get_data_path("works", work_id, "episodes", episode_id)
    storyboard_path = os.path.join(episode_path, "storyboard.json")
    storyboard = load_json(storyboard_path) or {}
    
    if "shots" not in storyboard:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    
    # 更新 storyboard 中的分镜数据
    shot_found = False
    for shot in storyboard["shots"]:
        if shot.get("id") == shot_id:
            shot_found = True
            if description is not None:
                shot["description"] = description
            if image_prompt is not None:
                shot["image_prompt"] = image_prompt
            if video_prompt is not None:
                shot["video_prompt"] = video_prompt
            if audio_prompt is not None:
                shot["audio_prompt"] = audio_prompt
            if duration is not None:
                try:
                    shot["duration"] = int(duration)
                except:
                    pass
            if reference_video_prompt is not None:
                shot["reference_video_prompt"] = reference_video_prompt
            if dialogue_prompt is not None:
                shot["dialogue_prompt"] = dialogue_prompt
            if video_task_id is not None:
                shot["video_task_id"] = video_task_id
            if current_video is not None:
                shot["current_video"] = current_video
            if video_history is not None:
                try:
                    shot["video_history"] = json.loads(video_history)
                except:
                    pass
            break
    
    if not shot_found:
        raise HTTPException(status_code=404, detail="Shot not found")
    
    save_json(storyboard_path, storyboard)
    
    # 同时更新分镜的 meta.json（如果存在）
    shot_path = get_shot_path(work_id, episode_id, shot_id)
    meta_path = os.path.join(shot_path, "meta.json")
    if os.path.exists(meta_path):
        meta = load_json(meta_path) or {}
        if description is not None:
            meta["description"] = description
        if image_prompt is not None:
            meta["image_prompt"] = image_prompt
        if video_prompt is not None:
            meta["video_prompt"] = video_prompt
        if audio_prompt is not None:
            meta["audio_prompt"] = audio_prompt
        save_json(meta_path, meta)
    
    return {"message": "Shot updated", "shot_id": shot_id}


async def call_llm_generate_prompts(description: str) -> dict:
    """
    调用LLM接口，根据分镜描述生成图片、视频、音频提示词
    目前是mock实现
    
    Args:
        description: 分镜描述
        
    Returns:
        {
            "image_prompt": "图片提示词",
            "video_prompt": "视频提示词",
            "audio_prompt": "音频提示词"
        }
    """
    # TODO: 实际调用LLM API
    # 示例：调用 LLM API
    # response = await llm_client.generate(
    #     prompt=f"请根据以下分镜描述生成图片提示词、视频提示词和音频提示词：\n{description}",
    #     ...
    # )
    # return {
    #     "image_prompt": response.image_prompt,
    #     "video_prompt": response.video_prompt,
    #     "audio_prompt": response.audio_prompt
    # }
    
    # Mock返回：返回3句占位的话
    return {
        "image_prompt": "",
        "video_prompt": "",
        "audio_prompt": ""
    }


def parse_single_shot_storyboard(text: str) -> Dict[str, Any]:
    """
    解析单镜头分镜脚本格式
    
    格式：
    剧本关联素材：素材1，素材2，素材3
    分镜1: 分镜描述文本
    关联素材: 素材1，素材2
    时长: 5
    分镜2: 分镜描述文本
    关联素材: 素材3
    时长: 6
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    result = {
        "related_materials": [],
        "shots": []
    }
    
    if not lines:
        return result
    
    # 解析第一行：剧本关联素材
    if lines[0].startswith('剧本关联素材：'):
        materials_str = lines[0].replace('剧本关联素材：', '').strip()
        result["related_materials"] = [m.strip() for m in materials_str.split('，') if m.strip()]
        lines = lines[1:]  # 移除第一行
    
    # 解析分镜（每4行为一个分镜：分镜N、关联素材、时长、空行）
    i = 0
    while i < len(lines):
        line = lines[i]
        # 匹配"分镜N:"
        match = re.match(r'^分镜\s*(\d+)\s*[:：]\s*(.*)$', line)
        if match:
            shot_num = match.group(1)
            description = match.group(2).strip()
            related_materials = []
            duration = 0
            
            # 下一行应该是关联素材
            if i + 1 < len(lines) and lines[i + 1].startswith('关联素材:'):
                materials_str = lines[i + 1].replace('关联素材:', '').strip()
                related_materials = [m.strip() for m in materials_str.split('，') if m.strip()]
                i += 1
            
            # 再下一行应该是时长
            if i + 1 < len(lines) and lines[i + 1].startswith('时长:'):
                duration_str = lines[i + 1].replace('时长:', '').strip()
                try:
                    duration = int(duration_str)
                except:
                    duration = 0
                i += 1
            
            result["shots"].append({
                "number": int(shot_num),
                "description": description,
                "related_materials": related_materials,
                "duration": duration
            })
        
        i += 1
    
    return result


@router.post("/{work_id}/{episode_id}/confirm-storyboard")
async def confirm_storyboard(work_id: str, episode_id: str):
    """生成分镜卡片（解析分镜脚本并调用LLM生成提示词）"""
    episode_path = get_data_path("works", work_id, "episodes", episode_id)
    
    # 确保剧集目录存在
    if not os.path.exists(episode_path):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Episode not found")
    
    storyboard_path = os.path.join(episode_path, "storyboard.json")
    storyboard = load_json(storyboard_path) or {}
    
    if not storyboard.get("text"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Storyboard text not found")
    
    # 解析分镜脚本文本，生成结构化数据
    text = storyboard["text"]
    shots = []
    related_materials = []
    
    # 尝试解析新格式（单镜头分镜脚本格式）
    try:
        parsed = parse_single_shot_storyboard(text)
        if parsed["shots"]:
            # 新格式解析成功
            related_materials = parsed["related_materials"]
            for shot_info in parsed["shots"]:
                description = shot_info["description"]
                shot_related_materials = shot_info.get("related_materials", [])
                duration = shot_info.get("duration", 0)
                
                # 创建分镜，提示词默认为空，用户可手动生成
                shot_data = {
                    "id": generate_id(),
                    "order": shot_info["number"],
                    "description": description,
                    "related_materials": shot_related_materials,
                    "duration": duration,
                    "image_prompt": "",
                    "video_prompt": "",
                    "audio_prompt": "",
                    "reference_video_prompt": "",
                    "dialogue_prompt": ""
                }
                
                shots.append(shot_data)
    except Exception as e:
        # 新格式解析失败，使用旧格式解析
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"新格式解析失败，使用旧格式: {e}")
        
        # 按分镜分割文本（支持"分镜1:"和"分镜 1:"两种格式）
        shot_blocks = re.split(r'\n分镜\s*\d+[:：]?\s*\n?', text)
        
        # 如果第一个块为空，移除它
        if shot_blocks and not shot_blocks[0].strip():
            shot_blocks = shot_blocks[1:]
        
        # 如果正则分割失败，尝试按"分镜"关键字分割
        if len(shot_blocks) <= 1:
            shot_blocks = re.split(r'分镜\s*\d+[:：]?\s*\n?', text)
            if shot_blocks and not shot_blocks[0].strip():
                shot_blocks = shot_blocks[1:]
        
        # 如果还是只有一个块，说明格式可能是"分镜1: 描述内容"（没有换行）
        if len(shot_blocks) <= 1:
            # 尝试按"分镜"关键字分割，但保留分隔符
            parts = re.split(r'(分镜\s*\d+[:：]?\s*)', text)
            shot_blocks = []
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    shot_blocks.append(parts[i] + parts[i + 1])
        
        for idx, block in enumerate(shot_blocks):
            if not block.strip():
                continue
            
            # 提取分镜描述（去除"分镜X:"前缀）
            description = re.sub(r'^分镜\s*\d+[:：]?\s*', '', block.strip())
            description = description.strip()
            
            if not description:
                continue
            
            # 创建分镜，提示词默认为空，用户可手动生成
            shot_data = {
                "id": generate_id(),
                "order": idx + 1,
                "description": description,
                "related_materials": [],
                "duration": 0,
                "image_prompt": "",
                "video_prompt": "",
                "audio_prompt": "",
                "reference_video_prompt": "",
                "dialogue_prompt": ""
            }
            
            shots.append(shot_data)
    
    # 如果解析失败，至少创建一个分镜
    if not shots:
        description = text.strip()[:200]
        shots.append({
            "id": generate_id(),
            "order": 1,
            "description": description,
            "related_materials": [],
            "duration": 0,
            "image_prompt": "",
            "video_prompt": "",
            "audio_prompt": "",
            "reference_video_prompt": "",
            "dialogue_prompt": ""
        })
    
    # 更新 storyboard
    storyboard["shots"] = shots
    storyboard["confirmed"] = True
    storyboard["related_materials"] = related_materials
    
    save_json(storyboard_path, storyboard)
    
    return storyboard

