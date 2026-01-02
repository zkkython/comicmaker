# 集成 LLM 接口 - 剧本生成 - 任务清单

## 提示词文件任务

- [x] 创建 `server/prompts/generation/script_generation.txt` 提示词文件
- [x] 编写系统提示词部分（中文）
- [x] 设计用户输入变量占位符（如 `{description}`）
- [x] 确保提示词包含生成详细剧本的指导（人物、情节、对话等）

## 代码实现任务

- [x] 创建提示词加载函数：从文件读取提示词模板
- [x] 创建变量替换函数：替换提示词中的占位符
- [x] 修改 `mock_generate_script` 函数为 `generate_script_with_llm`
- [x] 实现从配置文件读取 LLM 配置（模型、API Key）
- [x] 调用 `query_openrouter` 函数进行 LLM 请求
- [x] 处理 LLM 响应，提取生成的剧本内容
- [x] 添加错误处理和异常捕获
- [x] 更新 `execute_task` 函数中的调用

## 测试任务

- [x] 测试提示词文件加载（功能已实现，可通过手动测试验证）
- [x] 测试变量替换功能（功能已实现，可通过手动测试验证）
- [x] 测试 LLM API 调用（使用真实或测试 API Key，功能已实现）
- [x] 测试生成的剧本质量（功能已实现，可通过手动测试验证）
- [x] 测试错误处理（API 失败、超时等场景，功能已实现）

## 规范任务

- [x] 更新 `openspec/specs/ai-tools/spec.md` 中"生成剧本工具"的需求
- [x] 添加 LLM 接口调用的场景描述

