# 下载视频到本地管理

## 变更 ID
`download-videos-to-local`

## 目的
将所有 AI 生成的视频下载到本地服务器进行管理，替换直接使用外部 URL 的方式，确保视频资源的持久性和可控性。

## 为什么
- 当前系统直接使用 AI 接口返回的视频 URL（如 CloudFront CDN 链接）
- 这些外部 URL 可能会失效，导致视频无法访问
- 视频资源分散在外部服务，无法统一管理
- 分镜、历史记录、任务数据中都存储了外部 URL，存在数据丢失风险

## 变更内容

### 1. 视频下载功能
- 创建通用的视频下载函数，支持从 URL 下载视频到本地
- 为所有视频生成接口添加下载功能
- 下载后的视频保存到合适的本地路径，并生成本地访问 URL

### 2. 修改视频生成流程
- 修改 `vidu_reference_to_video_q2`、`sora_2_image_to_video`、`wan_2_6_image_to_video` 等接口
- 在视频生成成功后，自动下载视频到本地
- 将本地路径替换原始的外部 URL
- 更新任务输出和历史记录，使用本地 URL

### 3. 分镜视频存储
- 分镜生成的视频应保存到 `data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/` 目录
- 更新 `current_video` 字段为本地路径或 URL
- 更新 `video_history` 中的 `video_path` 为本地路径

### 4. 历史记录和任务视频存储
- 工具生成的视频应保存到 `data/tools/outputs/{tool_type}/{output_id}/` 目录
- 更新历史记录和任务输出中的 `video_url` 为本地路径或 URL

### 5. 数据迁移脚本
- 创建工具脚本扫描所有现有数据
- 识别所有外部视频 URL（CloudFront 等）
- 下载这些视频到本地
- 更新数据文件中的 URL 为本地路径
- 支持扫描：分镜数据（storyboard.json）、历史记录、任务数据

## 背景
- 项目已有图片下载功能（`download_image` 函数）
- 视频生成接口返回外部 URL，未下载到本地
- 分镜、历史记录、任务数据中都可能包含外部视频 URL
- 需要确保视频资源的持久性和可访问性

## 变更范围
- **后端代码**：
  - 修改 `server/utils/video_api.py`（添加视频下载功能）
  - 修改 `server/api/tools.py`（在任务执行后下载视频）
  - 修改 `server/api/content.py`（分镜视频处理）
- **工具脚本**：
  - 创建 `server/scripts/migrate_videos_to_local.py`（数据迁移脚本）

## 技术细节
- 使用 `requests` 库下载视频（流式下载，避免内存问题）
- 视频文件命名：使用时间戳和原始文件名
- 本地 URL 格式：`/data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/{filename}` 或 `/data/tools/outputs/{tool_type}/{output_id}/{filename}`
- 迁移脚本应支持批量处理和错误处理
- 迁移脚本应记录处理日志，便于排查问题

