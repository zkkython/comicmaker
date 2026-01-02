# 设计文档

## API 参数映射

### vidu/reference-to-video-q2
- **API URL**: `https://api.wavespeed.ai/api/v3/vidu/reference-to-video-q2`
- **请求参数**:
  - `aspect_ratio`: "1:1" | "3:4" | "4:3" | "16:9" | "9:16"
  - `resolution`: "540p" | "720p" | "1080p"
  - `duration`: 1-10 (整数)
  - `movement_amplitude`: "auto" (固定值)
  - `seed`: 0 (默认值)
  - `images`: 图片数组（最多7张，需要 base64 编码或 OSS URL）

### openai/sora-2/image-to-video
- **API URL**: `https://api.wavespeed.ai/api/v3/openai/sora-2/image-to-video`
- **请求参数**:
  - `duration`: 4 | 8 | 12 (整数)
  - `image`: 单张图片（需要 base64 编码或 OSS URL）

### alibaba/wan-2.5/image-to-video
- **API URL**: `https://api.wavespeed.ai/api/v3/alibaba/wan-2.5/image-to-video`
- **请求参数**:
  - `resolution`: "480p" | "720p" | "1080p"
  - `duration`: 3-10 (整数)
  - `enable_prompt_expansion`: boolean
  - `seed`: -1 (默认值)
  - `image`: 单张图片（需要 base64 编码或 OSS URL）

### alibaba/wan-2.6/image-to-video
- **API URL**: `https://api.wavespeed.ai/api/v3/alibaba/wan-2.6/image-to-video`
- **请求参数**:
  - `resolution`: "480p" | "720p" | "1080p"
  - `duration`: 3-10 (整数)
  - `shot_type`: "single" (固定值)
  - `enable_prompt_expansion`: boolean
  - `seed`: -1 (默认值)
  - `image`: 单张图片（需要 base64 编码或 OSS URL）

## 图片处理策略

所有视频生成工具都需要处理图片输入：
1. **单图片工具**（sora、wan）：图片上传到 OSS，获取 URL 后传递给 API
2. **多图片工具**（vidu）：所有图片上传到 OSS，获取 URL 列表后按顺序传递给 API

## 工具类型枚举更新

```python
class ToolType(str, Enum):
    # ... 现有工具 ...
    VIDU_REF_IMAGE_TO_VIDEO = "vidu_ref_image_to_video"  # vidu参考生视频
    SORA_IMAGE_TO_VIDEO = "sora_image_to_video"  # sora生视频
    WAN_IMAGE_TO_VIDEO = "wan_image_to_video"  # wan图生视频
    # 移除或保留原有的 text_to_video、ref_image_to_video
```

## 前端工具定义更新

```javascript
const TOOLS = [
    // ... 现有工具 ...
    {
        id: 'vidu_ref_image_to_video',
        name: 'vidu参考生视频',
        description: '使用 vidu 模型根据参考图片和文字描述生成视频',
        icon: '🎞️'
    },
    {
        id: 'sora_image_to_video',
        name: 'sora生视频',
        description: '使用 sora 模型根据图片和文字描述生成视频',
        icon: '🎬'
    },
    {
        id: 'wan_image_to_video',
        name: 'wan图生视频',
        description: '使用 wan 模型根据图片和文字描述生成视频',
        icon: '🎥'
    },
    // ... 其他工具 ...
];
```

## 历史记录视频显示

在历史记录列表中，如果输出包含视频：
- 显示视频缩略图（第一帧）
- 点击可播放视频
- 显示视频时长和文件大小（如果可用）

## 做同款图片填充

对于视频生成工具，做同款时需要：
1. 检测输入中的图片路径（`image_path`、`image_paths`）
2. 将图片 URL 转换为 File 对象
3. 使用 DataTransfer API 填充到文件输入框
4. 触发 change 事件更新预览

