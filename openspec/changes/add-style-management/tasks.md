# 任务列表

## 1. 创建提示词模板
- [x] 创建 `server/prompts/generation/image_to_style_description.txt`
- [x] 提示词应明确要求返回风格描述（三渲二、3D国创、赛璐璐、3D Q版等）
- [x] 提示词应说明风格描述用于生图和生视频
- [x] 提示词应限制输出在 100 字以内

## 2. 实现"图生风格描述"后端接口
- [x] 在 `server/api/tools.py` 中添加 `ToolType.IMAGE_TO_STYLE_DESCRIPTION`
- [x] 实现 `generate_style_description_with_llm` 函数
  - [x] 加载提示词模板 `image_to_style_description.txt`
  - [x] 编码图片为 base64
  - [x] 调用 OpenRouter LLM 接口（多模态输入）
  - [x] 返回风格描述、请求参数、响应 JSON
- [x] 在 `execute_task` 中添加 `IMAGE_TO_STYLE_DESCRIPTION` 的处理逻辑
- [x] 在 `create_tool_task` 中添加 `IMAGE_TO_STYLE_DESCRIPTION` 的参数处理

## 3. 实现"图生风格描述"前端工具
- [x] 在 `apps/web/js/tools.js` 的 `TOOLS` 数组中添加"图生风格描述"工具（放在"图生描述"下面）
- [x] 在 `TOOL_FIELDS` 中定义表单字段（图片上传、可选描述）
- [x] 在 `renderToolForm` 中使用标准图片上传组件（支持上传、粘贴、选择素材）
- [x] 在 `setupForm` 中处理表单提交
- [x] 在 `renderHistory` 中显示历史记录（包括输入图片和生成的风格描述）

## 4. 实现风格管理后端 API
- [x] 创建 `server/api/styles.py`
- [x] 实现 `get_styles` 接口（获取所有风格列表）
- [x] 实现 `get_style` 接口（获取单个风格详情）
- [x] 实现 `create_style` 接口（创建新风格）
  - [x] 接收名称、描述、参考图片
  - [x] 保存到 `data/styles/{style_id}/`
  - [x] 保存 `meta.json` 和 `reference.jpg`
- [x] 实现 `update_style` 接口（更新风格）
- [x] 实现 `delete_style` 接口（删除风格）
- [x] 实现 `get_style_image` 接口（获取风格参考图片，类似素材图片接口）

## 5. 实现风格管理前端页面
- [x] 创建 `apps/web/styles.html`
  - [x] 添加导航栏
  - [x] 添加风格列表区域
  - [x] 添加"创建新风格"按钮
  - [x] 添加创建/编辑风格对话框
- [x] 创建 `apps/web/js/styles.js`
  - [x] 实现风格列表加载和渲染
  - [x] 实现创建风格表单处理
  - [x] 实现编辑风格功能
  - [x] 实现删除风格功能（带确认）
  - [x] 实现"生成风格描述"按钮功能（调用图生风格描述接口）
  - [x] 集成标准图片上传组件（上传、粘贴、选择素材）
- [x] 创建 `apps/web/styles/styles.css`
  - [x] 风格列表网格布局样式
  - [x] 风格卡片样式
  - [x] 创建/编辑对话框样式
  - [x] 图片上传组件样式

## 6. 在作品详情页面集成风格选择
- [x] 修改 `apps/web/work-detail.html`
  - [x] 在风格描述字段旁边添加风格选择下拉框
  - [x] 下拉框显示"选择风格..."选项和所有已有风格
- [x] 修改 `apps/web/js/works.js`（或 `work-detail.html` 内联脚本）
  - [x] 加载风格列表到下拉框
  - [x] 实现风格选择逻辑（选择后填充风格描述字段）
  - [x] 在加载作品详情时，如果作品有风格描述，尝试匹配已有风格（可选）

## 7. 更新规范文档
- [x] 修改 `openspec/specs/ai-tools/spec.md`
  - [x] 添加"图生风格描述工具"需求
  - [x] 添加相关场景描述
- [x] 创建 `openspec/specs/style-management/spec.md`
  - [x] 定义风格管理的目的和范围
  - [x] 添加风格列表、创建、编辑、删除需求
  - [x] 添加风格选择需求
- [x] 修改 `openspec/specs/episode-management/spec.md`
  - [x] 在"作品详情编辑"需求中添加风格选择场景

## 8. 测试
- [ ] 测试"图生风格描述"工具（上传图片、生成描述）
- [ ] 测试风格管理功能（创建、编辑、删除）
- [ ] 测试"生成风格描述"按钮（在创建/编辑风格时）
- [ ] 测试作品详情页面的风格选择功能
- [ ] 测试选择风格后自动填充描述功能

