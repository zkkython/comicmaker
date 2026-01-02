# 设计文档

## 架构设计

### API 函数设计

#### 文生图 API 函数
三个模型使用不同的 API 接口和参数格式：

1. **seedream-v4.5**：
   - URL: `https://api.wavespeed.ai/api/v3/bytedance/seedream-v4.5/text-to-image`
   - 参数：`prompt`, `size` (格式: `"1024*1024"`)

2. **wan-2.6**：
   - URL: `https://api.wavespeed.ai/api/v3/alibaba/wan-2.6/text-to-image`
   - 参数：`prompt`, `size` (格式: `"1024*1024"`)

3. **nano-banana-pro**：
   - URL: `https://api.wavespeed.ai/api/v3/google/nano-banana-pro/text-to-image`
   - 参数：`prompt`, `aspect_ratio`, `resolution`

#### 图生图 API 函数
三个模型使用不同的 API 接口和参数格式：

1. **seedream-v4.5/edit**：
   - URL: `https://api.wavespeed.ai/api/v3/bytedance/seedream-v4.5/edit`
   - 参数：`prompt`, `images` (数组), `size` (格式: `"1024*1024"`)
   - 已有实现：`seedream_v4_edit` 函数

2. **wan-2.6/image-edit**：
   - URL: `https://api.wavespeed.ai/api/v3/alibaba/wan-2.6/image-edit`
   - 参数：`prompt`, `images` (数组), `size` (格式: `"1024*1024"`)

3. **nano-banana-pro/edit**：
   - URL: `https://api.wavespeed.ai/api/v3/google/nano-banana-pro/edit`
   - 参数：`prompt`, `images` (数组), `aspect_ratio`, `resolution`

### 分辨率计算逻辑

#### 比例到宽高的映射
- **1:1**：宽 = 高
- **3:4**：宽:高 = 3:4（竖图）
- **4:3**：宽:高 = 4:3（横图）
- **16:9**：宽:高 = 16:9（横图）
- **9:16**：宽:高 = 9:16（竖图）

#### 分辨率计算
- **1k**：短边 = 1024px（根据比例确定是宽还是高）
  - 1:1 → 1024*1024（宽=高=1024）
  - 3:4 → 768*1024（宽=768，高=1024，短边是宽）
  - 4:3 → 1024*768（宽=1024，高=768，短边是高）
  - 16:9 → 1820*1024（宽=1820，高=1024，短边是高）
  - 9:16 → 1024*1820（宽=1024，高=1820，短边是宽）
- **2k**：短边 = 2048px（根据比例确定是宽还是高）
  - 1:1 → 2048*2048（宽=高=2048）
  - 3:4 → 1536*2048（宽=1536，高=2048，短边是宽）
  - 4:3 → 2048*1536（宽=2048，高=1536，短边是高）
  - 16:9 → 3640*2048（宽=3640，高=2048，短边是高）
  - 9:16 → 2048*3640（宽=2048，高=3640，短边是宽）

### 前端交互设计

#### 文生图工具表单
```
- 文字描述输入框（textarea）
- 类型选择（人物/场景/道具）- 保留现有
- 模型选择（下拉框：seedream4.5、wan2.6、nanopro）
- 分辨率比例选择（下拉框：1:1, 3:4, 4:3, 16:9, 9:16）
- 分辨率选择（下拉框：1k、2k）
- 生成按钮
```

#### 图生图工具表单
```
- 文字描述输入框（textarea）
- 图片上传区域（支持多图片）
  - 每个图片显示缩略图
  - 每个图片有删除按钮
  - 支持拖拽排序
- 模型选择（下拉框：seedream4.5、wan2.6、nanopro）
- 分辨率比例选择（下拉框：1:1, 3:4, 4:3, 16:9, 9:16）
- 分辨率选择（下拉框：1k、2k）
- 生成按钮
```

#### 图片管理交互
- **上传**：使用 `image-upload.js` 工具，支持文件选择和粘贴
- **删除**：点击删除按钮，从列表中移除
- **排序**：使用 HTML5 Drag and Drop API
  - 拖拽时显示拖拽状态
  - 拖拽目标显示插入位置指示
  - 释放时更新图片顺序

### 数据流设计

#### 文生图任务流程
1. 用户填写表单（提示词、模型、比例、分辨率）
2. 前端提交到 `/api/tools/text_to_image/create`
3. 后端创建任务，调用对应的 API 函数
4. 根据模型类型计算参数（size 或 aspect_ratio + resolution）
5. 调用 Wavespeed API，轮询结果
6. 下载生成的图片，保存到 `data/tools/outputs/`
7. 更新任务状态，保存历史记录

#### 图生图任务流程
1. 用户填写表单（提示词、上传图片、模型、比例、分辨率）
2. 前端按顺序提交图片列表
3. 前端提交到 `/api/tools/image_to_image/create`
4. 后端创建任务，保存上传的图片（按顺序）
5. 调用对应的 API 函数，传入图片列表
6. 根据模型类型计算参数（size 或 aspect_ratio + resolution）
7. 调用 Wavespeed API，轮询结果
8. 下载生成的图片，保存到 `data/tools/outputs/`
9. 更新任务状态，保存历史记录

### 错误处理
- API 调用失败：返回错误信息，任务状态标记为失败
- 图片上传失败：提示用户重新上传
- 参数验证失败：返回 400 错误，提示用户检查输入
- 模型切换时验证参数兼容性

