# episode-management Specification

## 修改需求

### 需求：分镜视频下载到本地管理
系统必须将分镜生成的参考视频下载到本地服务器进行管理，替换直接使用外部 URL 的方式。

#### 场景：分镜参考视频生成后下载
- **当** 分镜生成参考视频成功
- **且** AI 接口返回视频 URL
- **则** 系统自动从 URL 下载视频到本地服务器
- **且** 视频保存到 `data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/reference_video_{timestamp}.mp4`
- **且** 分镜的 `current_video` 字段更新为本地路径（如 `/data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/reference_video_{timestamp}.mp4`）
- **且** `video_history` 中的 `video_path` 也更新为本地路径
- **且** 如果下载失败，记录错误日志但保留原始 URL

#### 场景：分镜视频访问
- **当** 用户预览分镜视频
- **且** 视频 URL 是本地路径
- **则** 系统通过本地文件服务提供视频访问
- **且** 视频可以正常播放

#### 场景：数据迁移
- **当** 系统运行数据迁移脚本
- **且** 扫描分镜数据（`storyboard.json`）
- **则** 识别所有外部视频 URL（如 CloudFront URL）
- **且** 下载这些视频到对应的分镜目录
- **且** 更新分镜数据中的 `current_video` 和 `video_history` 为本地路径
- **且** 记录迁移日志（成功、失败、跳过的数量）

