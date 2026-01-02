#!/usr/bin/env python3
"""
数据迁移脚本：将外部视频URL下载到本地并更新数据文件
"""

import os
import sys
import json
import glob
import logging
from pathlib import Path
from datetime import datetime

# 添加 server 目录到路径（utils 模块在 server 目录下）
server_dir = Path(__file__).parent.parent
sys.path.insert(0, str(server_dir.parent))  # 项目根目录
sys.path.insert(0, str(server_dir))  # server 目录

# 尝试导入依赖
try:
    import requests
    import shutil
except ImportError:
    print("错误: 缺少必要的依赖库。请运行: pip install requests")
    sys.exit(1)

from utils import get_data_path, load_json, save_json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def download_video(video_url: str, save_path: str) -> dict:
    """
    从 URL 下载视频并保存到本地路径
    
    Args:
        video_url (str): 视频的 URL
        save_path (str): 本地保存路径（包含文件名）
    
    Returns:
        dict: 包含 success, local_path, error 的字典
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 发送 HTTP GET 请求，stream=True 避免将整个文件加载到内存
        response = requests.get(video_url, stream=True, timeout=300)
        
        # 检查请求是否成功（状态码 200）
        response.raise_for_status()
        
        # 以二进制写入模式打开本地文件并保存内容
        with open(save_path, 'wb') as out_file:
            # 使用 shutil.copyfileobj 进行高效的流式下载
            shutil.copyfileobj(response.raw, out_file)
        
        logger.info(f"视频下载成功: {video_url} -> {save_path}")
        return {
            'success': True,
            'local_path': save_path
        }
    except Exception as e:
        logger.error(f"视频下载失败: {video_url} -> {save_path}, 错误: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def is_external_url(url: str) -> bool:
    """判断是否为外部URL"""
    if not url or not isinstance(url, str):
        return False
    return url.startswith('http://') or url.startswith('https://')


def download_video_for_shot(work_id: str, episode_id: str, shot_id: str, video_url: str) -> str:
    """下载视频到分镜目录"""
    shot_path = get_data_path("works", work_id, "episodes", episode_id, "shots", shot_id)
    videos_dir = os.path.join(shot_path, "videos")
    os.makedirs(videos_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    video_filename = f"reference_video_{timestamp}.mp4"
    video_path = os.path.join(videos_dir, video_filename)
    
    # 检查文件是否已存在
    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        logger.info(f"视频已存在，跳过: {video_path}")
        return f"/data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/{video_filename}"
    
    # 下载视频
    download_result = download_video(video_url, video_path)
    if download_result.get('success'):
        local_url = f"/data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/{video_filename}"
        logger.info(f"视频下载成功: {video_url} -> {local_url}")
        return local_url
    else:
        logger.error(f"视频下载失败: {video_url}, 错误: {download_result.get('error')}")
        return video_url  # 返回原始URL


def download_video_for_tool(tool_type: str, output_id: str, video_url: str) -> str:
    """下载视频到工具输出目录"""
    output_dir = get_data_path("tools", "outputs", tool_type, output_id)
    os.makedirs(output_dir, exist_ok=True)
    
    video_path = os.path.join(output_dir, "video.mp4")
    
    # 检查文件是否已存在
    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        logger.info(f"视频已存在，跳过: {video_path}")
        return f"/data/tools/outputs/{tool_type}/{output_id}/video.mp4"
    
    # 下载视频
    download_result = download_video(video_url, video_path)
    if download_result.get('success'):
        local_url = f"/data/tools/outputs/{tool_type}/{output_id}/video.mp4"
        logger.info(f"视频下载成功: {video_url} -> {local_url}")
        return local_url
    else:
        logger.error(f"视频下载失败: {video_url}, 错误: {download_result.get('error')}")
        return video_url  # 返回原始URL


def migrate_storyboard_videos():
    """迁移分镜数据中的视频"""
    logger.info("开始扫描分镜数据...")
    
    storyboard_files = glob.glob(
        str(get_data_path("works", "*", "episodes", "*", "storyboard.json"))
    )
    
    total_files = 0
    total_videos = 0
    success_count = 0
    fail_count = 0
    
    for storyboard_file in storyboard_files:
        try:
            storyboard = load_json(storyboard_file)
            if not storyboard or "shots" not in storyboard:
                continue
            
            total_files += 1
            updated = False
            
            for shot in storyboard.get("shots", []):
                # 检查 current_video
                if "current_video" in shot:
                    video_url = shot["current_video"]
                    if is_external_url(video_url):
                        total_videos += 1
                        # 从文件路径提取 work_id, episode_id, shot_id
                        parts = storyboard_file.split(os.sep)
                        work_idx = parts.index("works") + 1
                        episode_idx = parts.index("episodes") + 1
                        work_id = parts[work_idx]
                        episode_id = parts[episode_idx]
                        shot_id = shot.get("id")
                        
                        if shot_id:
                            local_url = download_video_for_shot(work_id, episode_id, shot_id, video_url)
                            shot["current_video"] = local_url
                            updated = True
                            if local_url != video_url:
                                success_count += 1
                            else:
                                fail_count += 1
                
                # 检查 video_history
                if "video_history" in shot and isinstance(shot["video_history"], list):
                    for history_item in shot["video_history"]:
                        if "video_path" in history_item:
                            video_url = history_item["video_path"]
                            if is_external_url(video_url):
                                total_videos += 1
                                parts = storyboard_file.split(os.sep)
                                work_idx = parts.index("works") + 1
                                episode_idx = parts.index("episodes") + 1
                                work_id = parts[work_idx]
                                episode_id = parts[episode_idx]
                                shot_id = shot.get("id")
                                
                                if shot_id:
                                    local_url = download_video_for_shot(work_id, episode_id, shot_id, video_url)
                                    history_item["video_path"] = local_url
                                    updated = True
                                    if local_url != video_url:
                                        success_count += 1
                                    else:
                                        fail_count += 1
            
            if updated:
                save_json(storyboard_file, storyboard)
                logger.info(f"已更新: {storyboard_file}")
        
        except Exception as e:
            logger.error(f"处理文件失败: {storyboard_file}, 错误: {str(e)}")
            fail_count += 1
    
    logger.info(f"分镜数据迁移完成: 扫描 {total_files} 个文件, 发现 {total_videos} 个视频, 成功 {success_count}, 失败 {fail_count}")


def migrate_history_videos():
    """迁移历史记录中的视频"""
    logger.info("开始扫描历史记录...")
    
    history_files = glob.glob(str(get_data_path("tools", "history", "*.json")))
    
    total_files = 0
    total_videos = 0
    success_count = 0
    fail_count = 0
    
    for history_file in history_files:
        try:
            record = load_json(history_file)
            if not record:
                continue
            
            total_files += 1
            updated = False
            
            # 检查 output.video_url
            if "output" in record and "video_url" in record["output"]:
                video_url = record["output"]["video_url"]
                if is_external_url(video_url):
                    total_videos += 1
                    tool_type = record.get("tool_type", "")
                    record_id = Path(history_file).stem
                    
                    local_url = download_video_for_tool(tool_type, record_id, video_url)
                    record["output"]["video_url"] = local_url
                    updated = True
                    if local_url != video_url:
                        success_count += 1
                    else:
                        fail_count += 1
            
            if updated:
                save_json(history_file, record)
                logger.info(f"已更新: {history_file}")
        
        except Exception as e:
            logger.error(f"处理文件失败: {history_file}, 错误: {str(e)}")
            fail_count += 1
    
    logger.info(f"历史记录迁移完成: 扫描 {total_files} 个文件, 发现 {total_videos} 个视频, 成功 {success_count}, 失败 {fail_count}")


def migrate_task_videos():
    """迁移任务数据中的视频"""
    logger.info("开始扫描任务数据...")
    
    task_files = glob.glob(str(get_data_path("tools", "tasks", "*.json")))
    
    total_files = 0
    total_videos = 0
    success_count = 0
    fail_count = 0
    
    for task_file in task_files:
        try:
            task = load_json(task_file)
            if not task:
                continue
            
            total_files += 1
            updated = False
            
            # 检查 output.video_url
            if "output" in task and task["output"] is not None and isinstance(task["output"], dict) and "video_url" in task["output"]:
                video_url = task["output"]["video_url"]
                if is_external_url(video_url):
                    total_videos += 1
                    tool_type = task.get("tool_type", "")
                    task_id = task.get("task_id", Path(task_file).stem)
                    
                    local_url = download_video_for_tool(tool_type, task_id, video_url)
                    task["output"]["video_url"] = local_url
                    updated = True
                    if local_url != video_url:
                        success_count += 1
                    else:
                        fail_count += 1
            
            if updated:
                save_json(task_file, task)
                logger.info(f"已更新: {task_file}")
        
        except Exception as e:
            logger.error(f"处理文件失败: {task_file}, 错误: {str(e)}")
            fail_count += 1
    
    logger.info(f"任务数据迁移完成: 扫描 {total_files} 个文件, 发现 {total_videos} 个视频, 成功 {success_count}, 失败 {fail_count}")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始视频数据迁移")
    logger.info("=" * 60)
    
    try:
        migrate_storyboard_videos()
        migrate_history_videos()
        migrate_task_videos()
        
        logger.info("=" * 60)
        logger.info("视频数据迁移完成")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"迁移过程发生错误: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
