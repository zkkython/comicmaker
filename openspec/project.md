# 项目上下文

## 目的
ComicMaker 是一个漫剧视频创作工具，使用户能够通过 AI 驱动的内容生成创建动画漫剧剧集。系统管理素材资源（人物角色、场景、道具），并提供从分镜生成到图片/视频/音频生成以及预览功能的完整工作流程。

## 技术栈
- **前端**：HTML + JavaScript + CSS（原生 Web 技术）
- **后端**：Python + FastAPI
- **数据存储**：JSON 文件（基于文本的存储）
- **AI 服务**：
  - **LLM 接口**：OpenRouter（用于脚本生成、分镜生成、提示词生成等）
  - **图片生成**：Wavespeed API（文本生成图片、图片生成图片）
  - **视频生成**：Wavespeed API（文本生成视频、图片生成视频、首尾帧生成视频）
  - **音频生成**：Wavespeed API（文本生成音频、语音合成）

## 项目约定

### 代码风格
- Python：遵循 PEP 8 规范
- JavaScript：使用 ES6+ 特性，优先使用 const/let 而非 var
- 使用有意义的变量和函数名
- 为复杂逻辑添加注释

### 架构模式
- **前端**：使用模块化结构的原生 JS，无框架依赖
- **后端**：使用 FastAPI 的 RESTful API
- **数据存储**：
  - JSON 文件用于结构化数据（描述、脚本、元数据）
  - 文件系统用于媒体资源（图片、视频、音频）
  - 组织化的文件夹结构：`data/{works}/{episodes}/{shots}/`

### 文件组织
- **素材资源**：`data/materials/{type}/{id}/`
  - `{type}`：`characters`、`scenes`、`props`
  - 每个素材包含：`main.jpg`、`aux1.jpg`（可选）、`aux2.jpg`（可选）、`meta.json`
- **作品**：`data/works/{work_id}/`
  - `meta.json`：作品元数据（名称、描述、封面图片、风格、宽高比）
  - `episodes/{episode_id}/`
    - `meta.json`：剧集元数据（名称、描述、封面）
    - `script.json`：原始脚本和预期时长
    - `storyboard.json`：生成的结构化分镜脚本
    - `shots/{shot_id}/`
      - `meta.json`：分镜元数据（描述、提示词）
      - `images/`：生成的候选图片
      - `videos/`：生成的视频
      - `audio/`：生成的音频文件
      - `history/`：历史生成记录
- **AI 工具数据**：`data/tools/`
  - `tasks/{task_id}.json`：任务数据
  - `history/{record_id}.json`：历史记录
  - `outputs/{tool_type}/{output_id}/`：生成的内容文件
- **AI 配置**：`server/config/`
  - `config.yaml`：AI 服务配置（LLM、图片生成、视频生成、音频生成等）
- **提示词模板**：`server/prompts/`
  - `generation/`：内容生成相关的提示词模板
    - `storyboard_gen/`：分镜生成提示词
    - `audio_prompt.txt`、`image_refine_prompt.txt`、`video_refine_prompt.txt` 等
  - `understanding/`：内容理解相关的提示词模板
    - `image_caption.txt`、`video_caption.txt`、`video_style_analysis.txt` 等

### 测试策略
- 后端：API 端点和业务逻辑的单元测试
- 前端：UI 交互的手动测试
- AI 服务调用的集成测试

### Git 工作流
- 主分支用于稳定发布
- 功能分支用于新功能开发
- 提交信息使用约定格式

## 领域上下文

### 素材管理
- **人物角色**：角色的视觉和音频表示
  - 主图 + 可选的辅助图片
  - 名称和描述
  - 音色设置（预留未来使用）
- **场景**：背景环境
  - 主图 + 可选的辅助图片
  - 名称和描述关键词
- **道具**：物品和对象
  - 主图 + 可选的辅助图片
  - 名称和描述关键词

### 剧集工作流
1. **脚本输入**：用户提供脚本文本和预期时长
2. **分镜生成**：LLM 从脚本生成结构化分镜脚本
3. **分镜卡片**：每个分镜包含：
   - 描述
   - 图片提示词
   - 视频提示词
   - 音频提示词（对话描述）
4. **内容生成**：
   - 每个分镜生成 3 张候选图片
   - 每个分镜生成 1 个视频
   - 每个分镜生成 1 个音频
   - 支持重新生成和历史浏览
5. **预览**：使用生成的内容预览剧集（如果有视频则播放视频，否则显示图片并持续预期时长）

## 重要约束
- 所有数据存储在文本文件（JSON）中 - 无需数据库
- 媒体资源按层次化文件夹结构组织
- 支持多种宽高比：9:16、16:9、4:3、3:4
- 前端必须无需构建工具即可工作（纯 HTML/JS/CSS）

## 外部依赖
- **OpenRouter API**：用于 LLM 调用（脚本生成、分镜生成、提示词生成等）
  - 配置位置：`server/config/config.yaml` 中的 `llm` 部分
  - 实现位置：`server/utils/query_llm.py` 中的 `query_openrouter` 函数
- **Wavespeed API**：用于图片生成、视频生成、音频生成
  - 配置位置：`server/config/config.yaml` 中的 `image_gen`、`video_gen`、`audio_gen` 部分
  - 实现位置：`server/utils/wavespeed_api.py`
  - 支持的功能：
    - 文本生成图片（text-to-image）
    - 图片生成图片（image-to-image）
    - 文本生成视频（text-to-video）
    - 图片生成视频（image-to-video）
    - 首尾帧生成视频（frame-to-frame）
    - 文本生成音频（text-to-audio）
    - 语音合成（speech synthesis）
