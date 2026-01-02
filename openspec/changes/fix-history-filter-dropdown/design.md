# 设计文档

## 架构决策

### 1. 动态生成筛选选项

筛选下拉框应该根据 `TOOLS` 数组动态生成，而不是硬编码。这样可以：
- 确保筛选选项与工具列表保持同步
- 当添加新工具时，筛选选项自动更新
- 避免手动维护两处工具列表

### 2. 实现方式

在 `tools.js` 中添加 `renderHistoryFilter()` 函数：

```javascript
function renderHistoryFilter() {
    const filterSelect = document.getElementById('history-filter');
    if (!filterSelect) return;
    
    // 清空现有选项（保留"全部工具"）
    filterSelect.innerHTML = '<option value="">全部工具</option>';
    
    // 根据 TOOLS 数组生成选项
    TOOLS.forEach(tool => {
        const option = document.createElement('option');
        option.value = tool.id;
        option.textContent = tool.name;
        filterSelect.appendChild(option);
    });
}
```

### 3. 初始化时机

在 `DOMContentLoaded` 事件中，在绑定筛选事件监听器之前调用 `renderHistoryFilter()`：

```javascript
document.addEventListener('DOMContentLoaded', () => {
    renderToolsList();
    setupForm();
    renderHistoryFilter(); // 生成筛选选项
    loadHistory();
    
    // 历史记录筛选
    document.getElementById('history-filter').addEventListener('change', (e) => {
        loadHistory(e.target.value);
    });
});
```

## 数据模型

### TOOLS 数组结构（已存在）

```javascript
const TOOLS = [
    {
        id: 'generate_script',
        name: '生成剧本',
        description: '...',
        icon: '📝'
    },
    // ... 其他工具
];
```

### 筛选下拉框结构

```html
<select id="history-filter" class="filter-select">
    <option value="">全部工具</option>
    <!-- 动态生成的选项 -->
    <option value="generate_script">生成剧本</option>
    <option value="generate_single_shot_storyboard">生成单镜头分镜脚本</option>
    <!-- ... -->
</select>
```

## UI/UX 设计

筛选下拉框的显示顺序应该与 `TOOLS` 数组中的顺序一致，保持与左侧工具列表的一致性。

## 边界情况处理

1. **TOOLS 数组为空**：
   - 只显示"全部工具"选项

2. **工具ID或名称缺失**：
   - 跳过该工具，不生成选项

3. **历史记录中的旧工具类型**：
   - 如果历史记录中存在旧的工具类型（如 `generate_storyboard`），筛选时可能无法匹配
   - 可以考虑在 `renderHistory` 函数中添加工具类型映射，将旧名称映射到新名称

