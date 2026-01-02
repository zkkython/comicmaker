# 设计文档

## 架构决策

### 1. 预览面板位置和布局

预览面板放置在"剧本关联素材"和"分镜管理"之间，使用独立的卡片区域：
- 使用 `card` 类保持与页面其他区域一致的样式
- 面板包含标题栏（带关闭按钮）和内容区域
- 内容区域使用单个 video 元素或 img 元素，根据当前分镜内容动态切换

### 2. 内容获取和优先级

每个分镜的内容获取逻辑：
1. 检查 `shot.current_video`（参考tab的视频）
2. 如果不存在，检查 `shot.video`（视频tab的视频）
3. 如果不存在，检查 `shot.selected_image`（已选择的图片）
4. 如果不存在，使用 `shot.image_candidates[0]`（第一张候选图片）

### 3. 连续播放实现

**视频播放：**
- 使用单个 `<video>` 元素
- 监听 `ended` 事件，当前视频结束后：
  - 获取下一个分镜的内容
  - 更新 video 元素的 `src` 属性
  - 调用 `play()` 方法开始播放

**图片显示：**
- 使用单个 `<img>` 元素或包含图片的容器
- 使用 `setTimeout` 在 `shot.duration * 1000` 毫秒后：
  - 清除当前定时器
  - 获取下一个分镜的内容
  - 更新显示内容
  - 如果是图片，设置新的定时器

### 4. 状态管理

- 使用全局变量 `isPreviewPanelVisible` 跟踪面板显示状态
- 使用全局变量 `previewTimer` 跟踪图片显示的定时器
- 使用全局变量 `currentPreviewIndex` 跟踪当前播放的分镜索引

### 5. 错误处理

- 视频加载失败：监听 `error` 事件，自动切换到下一个分镜
- 图片加载失败：使用 `onerror` 处理，显示占位符或跳过
- 分镜没有内容：显示占位符文本，持续1秒后切换到下一个

## 数据模型

### 分镜数据结构（已存在）

```json
{
  "id": "shot_id",
  "order": 1,
  "description": "分镜描述",
  "duration": 5,
  "current_video": "video_url",  // 参考tab的视频
  "video": "video_path",         // 视频tab的视频
  "selected_image": "image_path", // 已选择的图片
  "image_candidates": [
    {"path": "candidate_1.jpg"},
    {"path": "candidate_2.jpg"},
    {"path": "candidate_3.jpg"}
  ]
}
```

## UI/UX 设计

### 预览面板布局

```
┌─────────────────────────────────────┐
│ 剧集预览                    [×]     │
├─────────────────────────────────────┤
│                                     │
│      [视频/图片内容区域]            │
│                                     │
└─────────────────────────────────────┘
```

### 交互流程

1. 用户点击"预览剧集"按钮
2. 如果面板隐藏，显示面板并开始播放
3. 如果面板显示，隐藏面板并停止播放
4. 用户点击关闭按钮，隐藏面板并停止播放
5. 再次点击"预览剧集"按钮，重新显示面板并开始播放

## 技术实现细节

### HTML 结构

```html
<!-- 预览面板区域 -->
<div class="card" id="preview-panel" style="display: none;">
    <div class="card-header">
        <h2 class="card-title">剧集预览</h2>
        <button class="btn btn-sm btn-secondary" id="close-preview-btn">关闭</button>
    </div>
    <div class="card-body" id="preview-panel-content">
        <!-- 视频或图片将在这里动态显示 -->
    </div>
</div>
```

### JavaScript 逻辑

1. **显示/隐藏面板：**
   ```javascript
   function togglePreviewPanel() {
       const panel = document.getElementById('preview-panel');
       if (panel.style.display === 'none') {
           panel.style.display = 'block';
           startPreview();
       } else {
           panel.style.display = 'none';
           stopPreview();
       }
   }
   ```

2. **开始预览：**
   ```javascript
   function startPreview() {
       currentPreviewIndex = 0;
       playNextShot();
   }
   ```

3. **播放下一个分镜：**
   ```javascript
   async function playNextShot() {
       if (currentPreviewIndex >= currentShots.length) {
           // 预览结束
           return;
       }
       
       const shot = currentShots[currentPreviewIndex];
       const content = getShotContent(shot); // 按优先级获取内容
       
       if (content.type === 'video') {
           // 播放视频
       } else if (content.type === 'image') {
           // 显示图片
       }
   }
   ```

## 边界情况处理

1. **所有分镜都没有内容：**
   - 显示提示信息："暂无可预览的内容"
   - 不显示视频或图片

2. **部分分镜没有内容：**
   - 跳过没有内容的分镜
   - 继续播放下一个有内容的分镜

3. **视频加载失败：**
   - 监听 `error` 事件
   - 自动切换到下一个分镜

4. **图片加载失败：**
   - 使用 `onerror` 处理
   - 显示占位符，持续1秒后切换到下一个分镜

5. **分镜顺序问题：**
   - 确保按 `shot.order` 或数组索引顺序播放
   - 如果 `order` 字段存在，按 `order` 排序

