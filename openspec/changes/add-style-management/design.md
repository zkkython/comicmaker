# 设计文档

## 架构决策

### 1. 风格数据存储
风格数据存储在 `data/styles/{style_id}/` 目录，与素材管理保持一致的结构：
- `meta.json`：包含 `name`（名称）、`description`（描述）、`reference_image`（参考图片文件名）
- `reference.jpg`：参考图片文件（可选）

这种结构与素材管理（`data/materials/{type}/{id}/`）类似，便于统一管理和维护。

### 2. 图生风格描述工具
"图生风格描述"工具复用现有的 LLM 多模态接口，但使用专门的提示词模板：
- 提示词模板：`server/prompts/generation/image_to_style_description.txt`
- LLM 接口：与"图生描述"使用相同的 OpenRouter 多模态接口
- 主要区别：提示词明确要求返回风格描述，而非内容描述

### 3. 风格管理页面
风格管理页面参考素材管理页面的设计：
- 使用类似的网格布局展示风格列表
- 使用类似的创建/编辑对话框
- 复用图片上传组件（支持上传、粘贴、选择素材）

### 4. 作品风格选择
在作品详情编辑页面，风格选择下拉框位于风格描述字段旁边：
- 下拉框显示所有已有风格（按名称排序）
- 选择风格后，自动填充风格描述字段
- 用户可以基于填充的描述进行修改
- 如果作品已有风格描述，不自动匹配已有风格（保持简单）

## 数据模型

### 风格元数据（`meta.json`）
```json
{
  "name": "三渲二风格",
  "description": "三渲二风格，卡通渲染，色彩鲜艳，线条清晰...",
  "reference_image": "reference.jpg"
}
```

### 工具历史记录（`data/tools/history/{record_id}.json`）
"图生风格描述"工具的历史记录格式与其他工具类似：
```json
{
  "tool_type": "image_to_style_description",
  "input": {
    "image_path": "...",
    "user_description": "..."
  },
  "output": {
    "style_description": "...",
    "raw_content": "...",
    "api_request": {...},
    "api_response": {...},
    "prompt": {
      "system_prompt": "...",
      "user_message": "..."
    }
  },
  "created_at": "..."
}
```

## API 设计

### 风格管理 API（`/api/styles`）
- `GET /api/styles`：获取所有风格列表
- `GET /api/styles/{style_id}`：获取单个风格详情
- `POST /api/styles`：创建新风格
  - 参数：`name`（Form）、`description`（Form）、`reference_image`（File，可选）
- `PUT /api/styles/{style_id}`：更新风格
  - 参数：`name`（Form，可选）、`description`（Form，可选）、`reference_image`（File，可选）
- `DELETE /api/styles/{style_id}`：删除风格
- `GET /api/styles/{style_id}/image/{filename}`：获取风格参考图片

### 工具 API（`/api/tools`）
- 在 `create_tool_task` 中添加 `image_to_style_description` 工具类型
- 在 `execute_task` 中处理 `IMAGE_TO_STYLE_DESCRIPTION` 任务

## UI/UX 设计

### 风格管理页面
- 顶部：标题"风格管理"和"创建新风格"按钮
- 主体：风格列表网格（类似素材管理）
  - 每个风格卡片显示：参考图片（如果有）、名称、描述预览
  - 每个风格卡片有"编辑"和"删除"按钮

### 创建/编辑风格对话框
- 字段：
  - 风格名称（文本输入）
  - 风格描述（文本域）
  - 图片参考（图片上传组件，支持上传、粘贴、选择素材）
  - "生成风格描述"按钮（在图片参考下方）
- 操作：保存、取消

### 作品详情编辑页面
- 在"风格描述"字段旁边添加风格选择下拉框
- 下拉框显示"选择风格..."和所有已有风格
- 选择风格后，自动填充风格描述字段

## 提示词设计

### 图生风格描述提示词要点
1. 明确任务：根据图片生成风格描述
2. 说明用途：风格描述用于生图和生视频
3. 风格类型：三渲二、3D国创、赛璐璐、3D Q版等
4. 输出要求：详细描述风格特征，100字以内
5. 格式要求：直接输出描述文本，无需额外格式

