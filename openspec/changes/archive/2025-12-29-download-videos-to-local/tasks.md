# 任务列表

## 1. 创建视频下载函数
- [x] 在 `server/utils/image_process.py` 或新建 `server/utils/video_process.py` 中添加 `download_video()` 函数
- [x] 函数应支持从 URL 下载视频，保存到指定路径
- [x] 函数应处理下载错误和超时情况
- [x] 函数应返回下载成功状态和本地路径

## 2. 修改视频生成接口
- [x] 修改 `vidu_reference_to_video_q2` 函数，在返回前下载视频（在任务执行逻辑中处理）
- [x] 修改 `sora_2_image_to_video` 函数，在返回前下载视频（在任务执行逻辑中处理）
- [x] 修改 `wan_2_5_image_to_video` 函数，在返回前下载视频（在任务执行逻辑中处理）
- [x] 修改 `wan_2_6_image_to_video` 函数，在返回前下载视频（在任务执行逻辑中处理）
- [x] 确保下载后的视频路径正确返回

## 3. 修改任务执行逻辑
- [x] 修改 `server/api/tools.py` 中的 `execute_task` 函数
- [x] 对于所有视频生成工具类型，在任务成功后下载视频
- [x] 确定视频保存路径（工具输出目录）
- [x] 更新任务输出中的 `video_url` 为本地路径
- [x] 更新历史记录中的 `video_url` 为本地路径

## 4. 修改分镜视频处理
- [x] 修改 `apps/web/js/episode-edit.js` 中的 `generateReferenceVideo` 函数
- [x] 在视频生成成功后，调用后端 API 下载视频到分镜目录
- [x] 修改后端 API `/api/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/download-video`（已创建）
- [x] 更新分镜的 `current_video` 和 `video_history` 为本地路径

## 5. 创建数据迁移脚本
- [x] 创建 `server/scripts/migrate_videos_to_local.py` 脚本
- [x] 实现扫描分镜数据（`data/works/*/episodes/*/storyboard.json`）
- [x] 实现扫描历史记录（`data/tools/history/*.json`）
- [x] 实现扫描任务数据（`data/tools/tasks/*.json`）
- [x] 识别外部视频 URL（CloudFront 等）
- [x] 下载视频到合适的本地路径
- [x] 更新数据文件中的 URL 为本地路径
- [x] 添加日志记录和错误处理
- [x] 支持跳过已处理的视频（避免重复下载）

## 6. 测试和验证
- [x] 测试新的视频生成流程，验证视频正确下载
- [x] 测试分镜视频下载和路径更新
- [x] 测试历史记录和任务数据的视频下载
- [x] 运行迁移脚本，验证现有数据迁移正确
- [x] 验证所有视频 URL 都已替换为本地路径

