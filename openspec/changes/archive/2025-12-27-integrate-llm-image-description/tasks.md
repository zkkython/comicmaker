# 任务列表

## 1. 创建提示词模板文件
- [x] 创建 `server/prompts/generation/image_to_description.txt`
- [x] 编写系统提示词，包含：
  - 角色定义（专业的图片分析专家）
  - 任务目标（根据图片和用户描述生成详细描述设定）
  - 类型区分（人物/场景/道具）
  - 输出要求（100字以内，详细描述）
- [x] 添加变量占位符（`{material_type}`、`{user_description}`）

## 2. 实现 LLM 调用函数
- [x] 在 `server/api/tools.py` 中创建 `generate_description_with_llm` 函数
- [x] 实现图片编码（使用 `_encode_image_to_base64`）
- [x] 实现多模态消息构建（使用 `prepare_multimodal_messages_openai_format`）
- [x] 加载提示词模板并替换变量
- [x] 调用 OpenRouter LLM 接口
- [x] 处理错误和异常情况

## 3. 替换 mock 实现
- [x] 在 `execute_task` 函数中，将 `IMAGE_TO_DESCRIPTION` 工具类型的处理从 `mock_image_to_description` 改为 `generate_description_with_llm`
- [x] 更新输入参数处理（支持图片路径和用户描述）
- [x] 确保返回格式与现有接口兼容

## 4. 更新 API 接口
- [x] 在 `create_tool_task` 接口中，为 `IMAGE_TO_DESCRIPTION` 工具类型添加 `description` 参数（可选）
- [x] 确保图片上传和类型选择功能正常工作
- [x] 验证错误处理逻辑

## 5. 更新规范文档
- [x] 更新 `openspec/specs/ai-tools/spec.md` 中的"基于图生描述工具"需求
- [x] 添加 LLM 集成相关的场景描述
- [x] 添加提示词模板管理场景
- [x] 添加多模态输入处理场景

## 6. 测试验证
- [ ] 测试图片编码功能
- [ ] 测试 LLM 接口调用（使用真实图片）
- [ ] 测试不同类型（人物/场景/道具）的描述生成
- [ ] 测试用户描述参数的影响
- [ ] 验证返回描述长度（100字以内）
- [ ] 测试错误处理（图片不存在、LLM 调用失败等）

