# 集成 LLM 接口 - 图生描述

## 变更 ID
`integrate-llm-image-description`

## 目的
集成 OpenRouter LLM 接口，实现根据用户上传的图片和描述生成详细描述设定的功能。创建提示词模板文件，并替换现有的 mock 实现为真实的 LLM 调用。

## 为什么
当前"基于图生描述"工具使用的是 mock 实现，需要集成真实的 LLM 接口以提供实际的图片描述生成能力。这是三个 LLM 接口中的第二个，用于根据图片和用户描述生成详细的描述设定。

## 变更内容
1. 创建图生描述提示词模板文件（`server/prompts/generation/image_to_description.txt`）
2. 实现图片编码和多模态消息构建功能
3. 集成 OpenRouter LLM 接口调用（支持图片输入）
4. 替换 `server/api/tools.py` 中的 `mock_image_to_description` 为真实实现
5. 更新"基于图生描述"工具以使用真实 LLM 接口

## 背景
- 项目已配置 OpenRouter API（`server/config/config.yaml`）
- 已有 `query_openrouter` 函数实现（`server/utils/query_llm.py`）
- 已有图片编码函数 `_encode_image_to_base64`（`server/utils/query_llm.py`）
- 已有多模态消息构建函数 `prepare_multimodal_messages_openai_format`（`server/utils/query_llm.py`）
- 提示词文件应使用中文，支持变量替换（如 `{material_type}`、`{user_description}`）
- 返回格式为详细的描述文本，100字以内

## 变更范围
- **提示词文件**：新增 `server/prompts/generation/image_to_description.txt`
- **后端代码**：修改 `server/api/tools.py` 中的 `mock_image_to_description` 函数
- **工具函数**：使用现有的图片编码和多模态消息构建函数
- **规范**：修改 `openspec/specs/ai-tools/spec.md` 中的"基于图生描述工具"需求

## 技术细节
- LLM 接口需要支持多模态输入（图片 + 文本）
- 图片需要编码为 base64 格式
- 提示词需要根据用户选择的类型（人物/场景/道具）动态调整
- 用户可以提供额外的描述文本，用于指导生成方向
- 返回的描述应控制在 100 字以内

