# 设计文档

## 架构决策

### 1. 视频下载函数设计

创建一个通用的视频下载函数，类似于现有的 `download_image` 函数：

```python
def download_video(video_url: str, save_path: str) -> Dict[str, Any]:
    """
    从 URL 下载视频并保存到本地路径
    
    Args:
        video_url: 视频的 URL
        save_path: 本地保存路径（包含文件名）
    
    Returns:
        dict: 包含 success, local_path, error 的字典
    """
    try:
        response = requests.get(video_url, stream=True, timeout=300)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        return {
            'success': True,
            'local_path': save_path
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

### 2. 视频存储路径设计

#### 分镜视频
- 路径：`data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/{filename}`
- URL：`/data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/{filename}`
- 文件名：`video_{timestamp}_{original_filename}` 或 `reference_video_{timestamp}.mp4`

#### 工具生成的视频
- 路径：`data/tools/outputs/{tool_type}/{output_id}/video.mp4`
- URL：`/data/tools/outputs/{tool_type}/{output_id}/video.mp4`
- 文件名：`video.mp4` 或 `video_{timestamp}.mp4`

### 3. 视频生成接口修改

对于每个视频生成接口（如 `vidu_reference_to_video_q2`），在返回结果前：

1. 检查是否提供了 `save_path` 参数
2. 如果没有提供，根据工具类型和输出 ID 生成保存路径
3. 调用 `download_video` 下载视频
4. 如果下载成功，返回本地路径；如果失败，返回原始 URL 并记录错误

### 4. 任务执行流程修改

在 `server/api/tools.py` 的 `execute_task` 函数中：

1. 对于所有视频生成工具类型，在获取 `output_url` 后
2. 确定视频保存路径（基于工具类型和任务 ID）
3. 调用 `download_video` 下载视频
4. 更新 `output` 字典中的 `video_url` 为本地路径
5. 如果下载失败，记录错误但继续使用原始 URL

### 5. 分镜视频处理

在分镜生成参考视频时：

1. 前端调用工具生成视频（返回任务 ID）
2. 轮询任务状态，获取 `video_url`
3. 调用后端 API 下载视频到分镜目录
4. 更新分镜的 `current_video` 和 `video_history`

或者：

1. 前端调用工具生成视频（返回任务 ID）
2. 后端在任务执行时，如果检测到有 `work_id`、`episode_id`、`shot_id` 参数
3. 直接将视频下载到分镜目录
4. 返回本地路径

### 6. 数据迁移脚本设计

迁移脚本应：

1. **扫描数据源**：
   - 遍历 `data/works/*/episodes/*/storyboard.json`
   - 遍历 `data/tools/history/*.json`
   - 遍历 `data/tools/tasks/*.json`

2. **识别外部 URL**：
   - 检查 `current_video`、`video_url`、`video_path` 等字段
   - 识别 CloudFront URL（`d1q70pf5vjeyhc.cloudfront.net`）
   - 识别其他外部 CDN URL

3. **下载视频**：
   - 根据数据类型确定保存路径
   - 调用 `download_video` 下载
   - 处理下载失败的情况

4. **更新数据**：
   - 更新 JSON 文件中的 URL 字段
   - 保存更新后的文件

5. **日志和错误处理**：
   - 记录处理的文件数量
   - 记录成功和失败的下载
   - 支持跳过已处理的视频（检查本地文件是否存在）

## 数据模型

### 分镜视频数据结构

```json
{
  "current_video": "/data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/reference_video_20251229.mp4",
  "video_history": [
    {
      "video_path": "/data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/reference_video_20251229.mp4",
      "generated_at": "2025-12-29T10:00:00Z"
    }
  ]
}
```

### 历史记录数据结构

```json
{
  "output": {
    "video_url": "/data/tools/outputs/vidu_ref_image_to_video/{output_id}/video.mp4",
    "api_request": {...},
    "api_response": {...}
  }
}
```

## 边界情况处理

1. **下载失败**：
   - 记录错误日志
   - 保留原始 URL（向后兼容）
   - 允许后续重试

2. **视频文件已存在**：
   - 检查本地文件是否存在
   - 如果存在且大小合理，跳过下载
   - 如果不存在或损坏，重新下载

3. **磁盘空间不足**：
   - 检测可用空间
   - 如果空间不足，记录错误并跳过

4. **网络超时**：
   - 设置合理的超时时间（如 5 分钟）
   - 支持重试机制

5. **URL 格式识别**：
   - 支持多种外部 URL 格式
   - 正确识别 CloudFront、OSS 等 CDN URL

