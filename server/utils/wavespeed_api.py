"""
Wavespeed API 统一导入入口
为了保持向后兼容，此文件重新导出所有函数
实际实现已拆分到 image_api.py 和 video_api.py
"""

# 从 image_api 导入所有图片相关函数
from .image_api import (
    text_to_image_generate,
    image_to_image_generate,
    seedream_v4_5_text_to_image,
    wan_2_6_text_to_image,
    nano_banana_pro_text_to_image,
    seedream_v4_edit,
    wan_2_6_image_edit,
    nano_banana_pro_edit,
    seedream_v4_sequential_edit,
    calculate_image_size,
    calculate_image_size_wan26,
    generate_image_to_image_seedream,
    generate_image_to_image_wan26,
    generate_image_to_image_nanopro,
)

# 从 video_api 导入所有视频和音频相关函数
from .video_api import (
    text_to_video_generate,
    image_to_video_generate,
    frame_to_frame_video,
    hailuo_i2v_pro,
    runway_video_editing,
    vace_api,
    audio_gen,
    speech_gen,
    vidu_reference_to_video_q2,
    sora_2_image_to_video,
    wan_2_5_image_to_video,
    wan_2_6_image_to_video,
)

__all__ = [
    # 图片相关
    'text_to_image_generate',
    'image_to_image_generate',
    'seedream_v4_5_text_to_image',
    'wan_2_6_text_to_image',
    'nano_banana_pro_text_to_image',
    'seedream_v4_edit',
    'wan_2_6_image_edit',
    'nano_banana_pro_edit',
    'seedream_v4_sequential_edit',
    'calculate_image_size',
    'calculate_image_size_wan26',
    'generate_image_to_image_seedream',
    'generate_image_to_image_wan26',
    'generate_image_to_image_nanopro',
    # 视频相关
    'text_to_video_generate',
    'image_to_video_generate',
    'frame_to_frame_video',
    'hailuo_i2v_pro',
    'runway_video_editing',
    'vace_api',
    'audio_gen',
    'speech_gen',
    'vidu_reference_to_video_q2',
    'sora_2_image_to_video',
    'wan_2_5_image_to_video',
    'wan_2_6_image_to_video',
]
