# 任务列表

## 1. 实现 Wavespeed API 函数
- [x] 在 `server/utils/wavespeed_api.py` 中新增 `seedream_v4_5_text_to_image` 函数
- [x] 在 `server/utils/wavespeed_api.py` 中新增 `wan_2_6_text_to_image` 函数
- [x] 在 `server/utils/wavespeed_api.py` 中新增 `nano_banana_pro_text_to_image` 函数
- [x] 在 `server/utils/wavespeed_api.py` 中新增 `wan_2_6_image_edit` 函数
- [x] 在 `server/utils/wavespeed_api.py` 中新增 `nano_banana_pro_edit` 函数
- [x] 实现分辨率计算工具函数（根据比例和分辨率计算宽高）

## 2. 实现文生图工具后端
- [x] 在 `server/api/tools.py` 中修改 `TEXT_TO_IMAGE` 工具类型处理
- [x] 实现 `generate_text_to_image` 函数，支持模型切换
- [x] 实现分辨率参数处理（比例和分辨率选择）
- [x] 根据模型类型调用不同的 API 函数
- [x] 处理图片下载和保存
- [x] 更新 `create_tool_task` 接口，添加模型、比例、分辨率参数

## 3. 实现图生图工具后端
- [x] 在 `server/api/tools.py` 中新增 `IMAGE_TO_IMAGE` 工具类型
- [x] 实现 `generate_image_to_image` 函数，支持模型切换
- [x] 实现多图片输入处理（按顺序）
- [x] 实现分辨率参数处理（比例和分辨率选择）
- [x] 根据模型类型调用不同的 API 函数
- [x] 处理图片下载和保存
- [x] 更新 `create_tool_task` 接口，添加模型、比例、分辨率参数，支持多图片上传

## 4. 实现文生图工具前端
- [x] 在 `apps/web/js/tools.js` 中修改 `text_to_image` 工具表单定义
- [x] 添加模型选择下拉框（seedream4.5、wan2.6、nanopro）
- [x] 添加分辨率比例选择（1:1, 3:4, 4:3, 16:9, 9:16）
- [x] 添加分辨率选择（1k、2k）
- [x] 更新表单提交逻辑，包含新参数
- [x] 更新历史记录显示，包含模型和分辨率信息

## 5. 实现图生图工具前端
- [x] 在 `apps/web/js/tools.js` 中新增 `image_to_image` 工具定义
- [x] 在 `TOOLS` 数组中添加"图生图"工具（放在"文生图"下方）
- [x] 定义图生图工具表单字段（文本输入、多图片上传、模型选择、比例选择、分辨率选择）
- [x] 实现多图片上传和预览功能
- [x] 实现图片删除功能
- [x] 实现图片拖拽排序功能（使用 HTML5 Drag and Drop API）
- [x] 更新表单提交逻辑，按顺序提交图片
- [x] 更新历史记录显示，包含模型、分辨率和输入图片预览

## 6. UI 样式调整
- [x] 修改 `apps/web/styles/tools.css` 中的 `.tool-item` 样式，高度缩小 30%
- [x] 调整工具列表布局，确保缩小后仍美观
- [x] 添加图片列表容器样式
- [x] 添加拖拽排序相关样式（拖拽中、拖拽目标等）

## 7. 更新规范文档
- [x] 更新 `openspec/specs/ai-tools/spec.md` 中的"文生图工具"需求
- [x] 添加模型切换场景
- [x] 添加分辨率选择场景
- [x] 新增"图生图工具"需求
- [x] 添加多图片管理场景（上传、删除、排序）
- [x] 添加模型切换和分辨率选择场景

## 8. 测试验证
- [ ] 测试文生图工具的三个模型切换
- [ ] 测试文生图工具的不同分辨率和比例组合
- [ ] 测试图生图工具的三个模型切换
- [ ] 测试图生图工具的多图片上传和排序
- [ ] 测试图生图工具的图片删除功能
- [ ] 验证图片生成结果正确保存
- [ ] 验证历史记录正确显示

