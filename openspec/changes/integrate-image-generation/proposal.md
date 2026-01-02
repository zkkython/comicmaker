# 集成图片生成能力 - 文生图和图生图

## 变更 ID
`integrate-image-generation`

## 目的
实现文生图和图生图两个 AI 工具，接入多个图片生成模型（seedream、wan、banana），支持模型切换、分辨率选择和图片管理功能。

## 为什么
当前"文生图"工具使用的是 mock 实现，需要集成真实的图片生成 API。同时需要新增"图生图"工具，支持基于参考图片生成新图片的能力。这些功能是漫剧视频创作工具的核心能力之一。

## 变更内容
1. **文生图工具增强**：
   - 接入三个模型：bytedance/seedream-v4.5、alibaba/wan-2.6/text-to-image、google/nano-banana-pro/text-to-image
   - 支持在页面上切换模型（seedream4.5、wan2.6、nanopro），默认使用 seedream
   - 增加分辨率比例选择（1:1, 3:4, 4:3, 16:9, 9:16），默认 16:9
   - 增加分辨率选择（1k、2k），默认 1k
   - 根据模型类型和分辨率参数调用不同的 API 接口

2. **图生图工具（新增）**：
   - 新增"图生图"工具，放在"文生图"工具下方
   - 接入三个模型：bytedance/seedream-v4.5/edit、alibaba/wan-2.6/image-edit、google/nano-banana-pro/edit
   - 支持在页面上切换模型（seedream4.5、wan2.6、nanopro），默认使用 seedream
   - 支持上传或粘贴多张图片
   - 支持删除单张图片
   - 支持拖拽调整图片顺序
   - 提交时按照拖拽后的顺序提交
   - 支持分辨率比例和分辨率选择（与文生图相同）

3. **UI 调整**：
   - 左侧边栏工具列表每个 item 的高度缩小 30%

## 背景
- 项目已配置 Wavespeed API（`server/config/config.yaml`）
- 已有 `wavespeed_api.py` 中的图片生成相关函数
- 已有 `seedream_v4_edit` 函数实现（支持多图片输入）
- 需要新增 wan 和 banana 模型的 API 调用函数
- banana 的 API 传入比例和分辨率，wan 和 seedream 传入宽高
- 需要根据 1k/2k 和比例计算宽高值

## 变更范围
- **后端代码**：
  - 修改 `server/api/tools.py` 中的 `TEXT_TO_IMAGE` 工具实现
  - 新增 `IMAGE_TO_IMAGE` 工具类型和实现
  - 在 `server/utils/wavespeed_api.py` 中新增 wan 和 banana 模型的文生图和图生图函数
- **前端代码**：
  - 修改 `apps/web/js/tools.js` 中的工具定义和表单渲染
  - 修改 `apps/web/styles/tools.css` 中的工具列表样式
  - 实现图片上传、删除、拖拽排序功能
- **规范**：修改 `openspec/specs/ai-tools/spec.md` 中的"文生图工具"需求，新增"图生图工具"需求

## 技术细节
- **模型 API 差异**：
  - seedream 和 wan：使用 `size` 参数（格式：`"1024*1024"`），需要根据比例和分辨率计算宽高
  - banana：使用 `aspect_ratio` 和 `resolution` 参数
- **分辨率计算**：
  - 1k：短边 1024px，长边根据比例计算
  - 2k：短边 2048px，长边根据比例计算
  - 比例映射：1:1, 3:4, 4:3, 16:9, 9:16
- **图片管理**：
  - 使用 HTML5 Drag and Drop API 实现拖拽排序
  - 使用 `image-upload.js` 工具实现图片上传和粘贴
  - 维护图片列表的顺序状态

## 依赖关系
- 依赖现有的 `image-upload.js` 工具
- 依赖 Wavespeed API 配置
- 依赖现有的任务管理系统

