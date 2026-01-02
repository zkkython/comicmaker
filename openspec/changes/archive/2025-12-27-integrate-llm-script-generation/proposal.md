# 集成 LLM 接口 - 剧本生成

## 变更 ID
`integrate-llm-script-generation`

## 目的
集成 OpenRouter LLM 接口，实现根据用户描述生成详细剧本的功能。创建提示词模板文件，并替换现有的 mock 实现为真实的 LLM 调用。

## 为什么
当前"生成剧本"工具使用的是 mock 实现，需要集成真实的 LLM 接口以提供实际的剧本生成能力。这是三个 LLM 接口中的第一个，后续还将实现剧本生成分镜脚本和图片生成描述功能。

## 变更内容
1. 创建剧本生成提示词模板文件（`server/prompts/generation/script_generation.txt`）
2. 实现提示词加载和变量替换功能
3. 集成 OpenRouter LLM 接口调用
4. 替换 `server/api/tools.py` 中的 `mock_generate_script` 为真实实现
5. 更新"生成剧本"工具以使用真实 LLM 接口

## 背景
- 项目已配置 OpenRouter API（`server/config/config.yaml`）
- 已有 `query_openrouter` 函数实现（`server/utils/query_llm.py`）
- 提示词文件应使用中文，支持变量替换
- 返回格式为详细的剧本描述，包括人物、情节、对话等

## 变更范围
- **提示词文件**：新增 `server/prompts/generation/script_generation.txt`
- **后端代码**：修改 `server/api/tools.py` 中的 `mock_generate_script` 函数
- **工具函数**：可能需要添加提示词加载和替换的辅助函数
- **规范**：新增或修改 `openspec/specs/ai-tools/spec.md` 中的相关需求

## 主要改进
1. **真实 LLM 集成**：使用 OpenRouter 提供实际的剧本生成能力
2. **提示词模板化**：将提示词独立为文件，便于维护和优化
3. **变量替换支持**：提示词支持变量替换，提高灵活性

## 用户价值
- 提供真实的剧本生成功能
- 生成的剧本质量更高，更符合用户需求
- 为后续功能（分镜生成、图片描述）奠定基础

## 依赖关系
- 依赖 OpenRouter API 配置和 `query_openrouter` 函数
- 需要从配置文件读取 LLM 配置（模型、API Key）

## 风险评估
- 低风险：已有 OpenRouter 接口实现，只需集成
- 需要处理 API 调用失败、超时等异常情况
- 提示词质量需要测试和优化

