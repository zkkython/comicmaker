# 设计文档

## 架构设计

### 图片处理流程
1. 用户上传图片 → 保存到临时目录
2. 图片路径传递给 `generate_description_with_llm` 函数
3. 使用 `_encode_image_to_base64` 将图片编码为 base64
4. 构建多模态消息（图片 + 文本提示词）

### LLM 调用流程
1. 加载提示词模板（`server/prompts/generation/image_to_description.txt`）
2. 替换模板中的变量：
   - `{material_type}` → 用户选择的类型（人物/场景/道具）
   - `{user_description}` → 用户提供的额外描述（可选）
3. 使用 `prepare_multimodal_messages_openai_format` 构建消息：
   - 系统提示词（替换变量后的模板）
   - 用户消息（包含图片和用户描述）
4. 调用 OpenRouter API（使用 `query_openrouter` 或直接调用）
5. 解析返回结果，提取描述文本

### 提示词模板设计

#### 结构
- **角色定义**：专业的图片分析专家，擅长根据图片生成详细描述
- **任务目标**：根据图片和用户描述，生成详细的描述设定
- **类型区分**：根据用户选择的类型（人物/场景/道具），调整描述重点
- **输出要求**：
  - 描述应详细、准确
  - 控制在 100 字以内
  - 包含关键特征和细节

#### 变量
- `{material_type}`：用户选择的类型（人物/场景/道具）
- `{user_description}`：用户提供的额外描述（可选，如果用户没有提供则为空）

### 错误处理
- **图片不存在**：返回明确的错误信息
- **图片编码失败**：捕获异常并返回错误
- **LLM 调用失败**：捕获 API 错误，返回友好的错误信息
- **返回内容为空**：检查并返回错误

### 与现有代码的集成
- 复用 `server/utils/query_llm.py` 中的图片编码函数
- 复用 `server/utils/query_llm.py` 中的多模态消息构建函数
- 复用 `server/api/tools.py` 中的提示词加载和配置加载函数
- 保持与 `generate_script_with_llm` 类似的代码结构

## 实现细节

### 函数签名
```python
async def generate_description_with_llm(
    image_path: str,
    material_type: str,
    user_description: Optional[str] = None
) -> str
```

### 参数说明
- `image_path`：图片文件路径
- `material_type`：素材类型（"人物"、"场景"、"道具"）
- `user_description`：用户提供的额外描述（可选）

### 返回值
- 生成的描述文本（字符串，100字以内）

### 异常处理
- `FileNotFoundError`：图片文件不存在
- `Exception`：LLM 调用失败或其他错误

## 提示词模板示例结构

```
# 系统提示词

你是一位专业的图片分析专家，擅长根据图片内容生成详细的描述设定。你具有丰富的视觉分析经验，能够准确捕捉图片中的关键特征和细节。

## 任务目标

根据用户提供的图片和描述，生成一个详细的描述设定。描述应针对{material_type}类型的内容，包含关键特征、细节和视觉元素。

## 输出要求

- 描述应详细、准确，能够准确反映图片内容
- 描述应控制在 100 字以内
- 根据类型（{material_type}）调整描述重点：
  - 人物：外貌特征、服装、表情、姿态等
  - 场景：环境、氛围、光线、构图等
  - 道具：外观、材质、细节、用途等
- 如果用户提供了额外描述（{user_description}），应结合用户描述和图片内容生成描述

## 输出格式

请直接输出生成的描述文本，无需额外的格式说明。描述应简洁明了，重点突出。

---

注意：用户将在下一条消息中提供图片和描述内容。
```

