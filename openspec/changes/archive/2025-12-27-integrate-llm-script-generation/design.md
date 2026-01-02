# 集成 LLM 接口 - 剧本生成 - 设计文档

## 架构决策

### 1. 提示词文件组织

**决策**：将提示词存储在独立的文本文件中，支持变量替换

**理由**：
- 便于维护和优化提示词，无需修改代码
- 支持多语言提示词（当前使用中文）
- 可以版本控制和单独测试提示词

**实现**：
- 文件位置：`server/prompts/generation/script_generation.txt`
- 变量格式：使用 `{variable_name}` 格式（如 `{description}`）
- 文件编码：UTF-8

### 2. 提示词结构

**决策**：使用系统提示词 + 用户输入的结构

**理由**：
- 符合 OpenRouter API 的消息格式要求
- 系统提示词定义角色和任务，用户输入提供具体内容
- 便于后续优化和调整

**实现**：
- 系统提示词：定义 AI 角色（专业编剧）、任务目标、输出要求
- 用户输入：包含用户提供的描述文本
- 变量替换：在系统提示词或用户输入中替换 `{description}`

### 3. LLM 配置管理

**决策**：从 `config.yaml` 读取 LLM 配置

**理由**：
- 配置集中管理，便于修改
- 支持不同环境使用不同配置
- 符合项目现有的配置管理方式

**实现**：
- 读取 `server/config/config.yaml` 中的 `llm` 部分
- 获取 `model` 和 `openai_api_key`（实际是 OpenRouter API Key）
- 使用 `query_openrouter` 函数进行调用

### 4. 错误处理

**决策**：捕获异常并返回友好的错误信息

**理由**：
- LLM API 调用可能失败（网络、认证、限流等）
- 需要向用户提供清晰的错误反馈
- 避免系统崩溃

**实现**：
- 捕获 `query_openrouter` 的异常
- 记录错误日志
- 返回包含错误信息的响应
- 任务状态标记为 `failed`

## 数据流

1. **用户提交描述**：
   - 用户在工具页面输入描述文本
   - 前端调用 `POST /api/tools/generate_script/create`

2. **创建任务**：
   - 后端创建任务，状态为 `pending`
   - 返回任务ID给前端

3. **执行 LLM 调用**：
   - 加载提示词模板文件
   - 替换变量（`{description}` → 用户输入）
   - 读取 LLM 配置
   - 调用 `query_openrouter` 函数
   - 提取生成的剧本内容

4. **保存结果**：
   - 将生成的剧本保存到任务输出
   - 更新任务状态为 `success`
   - 创建历史记录

5. **前端获取结果**：
   - 前端轮询任务状态
   - 任务完成后获取结果并显示

## API 设计

### 提示词文件格式

```
# 系统提示词
你是一位专业的编剧，擅长根据简短的描述创作详细的剧本。

# 任务目标
根据用户提供的描述，生成一个完整的剧集剧本。剧本应包含：
- 详细的人物设定和角色关系
- 完整的情节发展
- 具体的对话内容
- 场景描述和氛围营造

# 输出要求
- 剧本应详细、完整，能够直接用于后续的分镜制作
- 语言自然流畅，符合剧本写作规范
- 包含足够的细节，便于视觉化呈现

# 用户输入
{description}
```

### 函数签名

```python
async def generate_script_with_llm(description: str) -> str:
    """
    使用 LLM 根据描述生成剧本
    
    Args:
        description: 用户输入的描述文本
        
    Returns:
        生成的详细剧本文本
        
    Raises:
        Exception: LLM 调用失败时抛出异常
    """
```

### 配置读取

```python
def load_llm_config() -> dict:
    """
    从 config.yaml 加载 LLM 配置
    
    Returns:
        {
            "model": "openai/gpt-4o",
            "api_key": "..."
        }
    """
```

### 提示词加载和替换

```python
def load_prompt_template(template_path: str) -> str:
    """
    加载提示词模板文件
    
    Args:
        template_path: 模板文件路径
        
    Returns:
        模板内容字符串
    """

def replace_prompt_variables(template: str, **kwargs) -> str:
    """
    替换提示词模板中的变量
    
    Args:
        template: 模板字符串
        **kwargs: 变量名和值的映射
        
    Returns:
        替换后的字符串
    """
```

## 文件组织

```
server/
├── prompts/
│   └── generation/
│       └── script_generation.txt    # 新增：剧本生成提示词
├── config/
│   └── config.yaml                  # LLM 配置
├── utils/
│   └── query_llm.py                 # query_openrouter 函数
└── api/
    └── tools.py                     # 修改：集成 LLM 调用
```

## 向后兼容性

- 不影响其他工具的实现
- 如果 LLM 调用失败，可以考虑降级到 mock 实现（可选）
- 提示词文件不存在时，应提供清晰的错误信息

