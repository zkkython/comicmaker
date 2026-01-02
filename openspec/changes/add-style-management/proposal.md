# 添加风格管理和图生风格描述工具

## 变更 ID
`add-style-management`

## 目的
添加风格管理功能，允许用户创建、编辑和删除风格模板，并在作品创建/编辑时选择已有风格。同时添加"图生风格描述"AI 工具，根据图片生成风格描述，用于生图和生视频。

## 为什么
- 用户需要管理可复用的风格模板，避免每次创建作品时重复输入风格描述
- 用户需要根据参考图片自动生成风格描述，提高工作效率
- 风格描述是内容生成（图片、视频）的重要输入，需要统一管理和使用

## 变更内容
1. 添加"图生风格描述"AI 工具（放在"图生描述"工具下面）
   - 创建提示词模板文件 `server/prompts/generation/image_to_style_description.txt`
   - 实现后端接口调用（复用现有的 LLM 多模态接口）
   - 添加前端工具表单和结果展示
2. 创建风格管理功能
   - 创建风格列表页面（类似素材管理）
   - 实现风格的创建、编辑、删除功能
   - 风格包含：名称、描述、图片参考
   - 在创建/编辑风格时，可以调用"图生风格描述"接口生成描述
3. 在作品创建/编辑界面集成风格选择
   - 在风格描述字段旁边添加下拉框，选择已有风格
   - 选择风格后，自动填充风格描述字段
   - 用户可以基于填充的描述进行修改

## 背景
- 项目已实现素材管理功能，可以作为风格管理的参考
- 项目已实现"图生描述"工具，可以作为"图生风格描述"的参考
- 作品已有 `style_description` 字段，存储在 `meta.json` 中
- LLM 接口已支持多模态输入（图片 + 文本）

## 变更范围
- **提示词文件**：新增 `server/prompts/generation/image_to_style_description.txt`
- **后端代码**：
  - 新增 `server/api/styles.py`（风格管理 API）
  - 修改 `server/api/tools.py`（添加"图生风格描述"工具）
- **前端代码**：
  - 新增 `apps/web/styles.html`（风格管理页面）
  - 新增 `apps/web/js/styles.js`（风格管理逻辑）
  - 新增 `apps/web/styles/styles.css`（风格管理样式）
  - 修改 `apps/web/js/tools.js`（添加"图生风格描述"工具）
  - 修改 `apps/web/work-detail.html`（添加风格选择下拉框）
  - 修改 `apps/web/js/works.js`（处理风格选择逻辑）
- **数据存储**：新增 `data/styles/{style_id}/` 目录结构
- **规范**：
  - 修改 `openspec/specs/ai-tools/spec.md`（添加"图生风格描述"工具需求）
  - 新增 `openspec/specs/style-management/spec.md`（风格管理规范）
  - 修改 `openspec/specs/episode-management/spec.md`（添加风格选择需求）

## 技术细节
- 风格数据存储在 `data/styles/{style_id}/` 目录
  - `meta.json`：风格元数据（名称、描述）
  - `reference.jpg`：参考图片（可选）
- "图生风格描述"工具使用与"图生描述"相同的 LLM 接口，但使用不同的提示词模板
- 提示词应明确要求返回风格描述，包括三渲二、3D国创、赛璐璐、3D Q版等风格类型
- 风格描述应适合作为生图和生视频的输入提示词

