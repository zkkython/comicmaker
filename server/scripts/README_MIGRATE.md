# 视频数据迁移脚本使用说明

## 功能
将现有数据中的外部视频 URL（如 CloudFront CDN 链接）下载到本地服务器，并更新数据文件中的 URL 为本地路径。

## 前置条件

1. **安装 Python 依赖**：
   ```bash
   cd /Users/cloudy/comicmaker/server
   pip install -r requirements.txt
   ```
   
   或者如果使用 conda 环境：
   ```bash
   conda activate <your_env>
   cd /Users/cloudy/comicmaker/server
   pip install -r requirements.txt
   ```

2. **确保有足够的磁盘空间**：视频文件可能较大，请确保有足够的存储空间。

## 执行方式

### 方式一：直接执行脚本（推荐）

```bash
cd /Users/cloudy/comicmaker
python3 server/scripts/migrate_videos_to_local.py
```

### 方式二：使用 Python 模块方式

```bash
cd /Users/cloudy/comicmaker
python3 -m server.scripts.migrate_videos_to_local
```

## 脚本功能

脚本会扫描以下数据源：

1. **分镜数据** (`data/works/*/episodes/*/storyboard.json`)
   - 扫描 `current_video` 字段
   - 扫描 `video_history` 数组中的 `video_path` 字段

2. **历史记录** (`data/tools/history/*.json`)
   - 扫描 `output.video_url` 字段

3. **任务数据** (`data/tools/tasks/*.json`)
   - 扫描 `output.video_url` 字段

## 处理流程

1. **识别外部 URL**：检测以 `http://` 或 `https://` 开头的 URL
2. **下载视频**：将视频下载到对应的本地目录
   - 分镜视频：`data/works/{work_id}/episodes/{episode_id}/shots/{shot_id}/videos/reference_video_{timestamp}.mp4`
   - 工具视频：`data/tools/outputs/{tool_type}/{output_id}/video.mp4`
3. **更新数据**：将数据文件中的 URL 替换为本地路径
4. **跳过已存在**：如果本地文件已存在，跳过下载

## 输出日志

脚本会输出详细的日志信息，包括：
- 扫描的文件数量
- 发现的视频数量
- 成功下载的数量
- 失败的数量
- 每个文件的处理状态

## 注意事项

1. **备份数据**：建议在执行迁移前备份 `data` 目录
2. **网络连接**：确保可以访问外部视频 URL
3. **执行时间**：根据视频数量和大小，可能需要较长时间
4. **错误处理**：如果某个视频下载失败，脚本会记录错误但继续处理其他视频
5. **重复执行**：脚本支持重复执行，已下载的视频会被跳过

## 示例输出

```
============================================================
开始视频数据迁移
============================================================
开始扫描分镜数据...
已更新: data/works/xxx/episodes/xxx/storyboard.json
分镜数据迁移完成: 扫描 1 个文件, 发现 3 个视频, 成功 3, 失败 0
开始扫描历史记录...
已更新: data/tools/history/xxx.json
历史记录迁移完成: 扫描 10 个文件, 发现 5 个视频, 成功 5, 失败 0
开始扫描任务数据...
任务数据迁移完成: 扫描 20 个文件, 发现 8 个视频, 成功 8, 失败 0
============================================================
视频数据迁移完成
============================================================
```

