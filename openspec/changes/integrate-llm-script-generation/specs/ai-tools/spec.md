# AI 工具

## Purpose
提供统一的 AI 工具界面，包含多个 AI 生成工具，支持异步任务处理、状态轮询和历史记录管理。

## 修改需求

### 需求：生成剧本工具
系统必须使用 OpenRouter LLM 接口根据用户描述生成详细的剧本文本，替换现有的 mock 实现。

#### 场景：使用 LLM 生成剧本
- **当** 用户在工具页面使用"生成剧本"工具
- **且** 输入描述文本并提交
- **则** 系统加载提示词模板文件 `server/prompts/generation/script_generation.txt`
- **且** 将用户描述替换到提示词模板的变量位置
- **且** 从配置文件读取 LLM 配置（模型、API Key）
- **且** 调用 OpenRouter LLM 接口生成剧本
- **且** 返回生成的详细剧本文本（包含人物、情节、对话等）
- **且** 如果 LLM 调用失败，任务状态标记为失败并返回错误信息

#### 场景：提示词模板管理
- **当** 系统需要生成剧本时
- **则** 从 `server/prompts/generation/script_generation.txt` 加载提示词模板
- **且** 提示词使用中文编写
- **且** 提示词包含变量占位符（如 `{description}`）用于替换用户输入
- **且** 提示词应包含系统角色定义、任务目标和输出要求

#### 场景：LLM 配置读取
- **当** 系统需要调用 LLM 接口时
- **则** 从 `server/config/config.yaml` 读取 `llm` 配置
- **且** 获取 `model` 字段（LLM 模型名称）
- **且** 获取 `openai_api_key` 字段（OpenRouter API Key）
- **且** 使用这些配置调用 `query_openrouter` 函数

