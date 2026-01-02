# 设计文档

## 架构决策

### 1. 素材多选面板的实现方式

**决策**：基于现有的素材单选面板，扩展为多选面板组件

**理由**：
- 复用现有的代码和样式，减少开发工作量
- 保持UI/UX的一致性
- 可以同时支持单选和多选两种模式

**实现**：
- 在 `apps/web/js/tools.js` 中创建新的函数 `openMaterialMultiSelectDialog`
- 或者创建独立的 `material-multi-select.js` 文件
- 使用数组 `selectedMaterialIds` 存储选中的素材ID
- 在渲染时，检查素材ID是否在选中数组中，显示勾选状态

### 2. 素材关联数据的存储方式

**决策**：在作品的 `meta.json` 中存储素材ID列表

**理由**：
- 简单直接，无需额外的关联表
- 与现有的JSON存储方式一致
- 易于查询和更新

**实现**：
```json
{
  "name": "作品名称",
  "description": "作品描述",
  "character_materials": ["material_id_1", "material_id_2"],
  "scene_materials": ["material_id_3"],
  "prop_materials": ["material_id_4", "material_id_5"]
}
```

### 3. 素材详情的获取方式

**决策**：在加载作品时，根据素材ID列表批量获取素材详情

**理由**：
- 避免多次API调用
- 可以一次性获取所有关联素材的完整信息
- 如果素材被删除，可以优雅处理（显示"已删除"或跳过）

**实现**：
- 在 `server/api/materials.py` 中添加批量获取接口（可选）
- 或者在前端循环调用单个素材获取接口
- 在作品详情页面显示时，如果素材不存在，显示占位符或跳过

### 4. 跳转到素材管理页面的处理

**决策**：使用 URL 参数传递当前筛选的类型，返回时保持作品详情页面状态

**理由**：
- 用户可以在创建素材后，直接返回作品详情页面
- 通过 URL 参数，素材管理页面可以自动打开对应类型的创建面板

**实现**：
- 跳转时使用 `materials.html?type=characters&return=work-detail.html?work_id=xxx`
- 素材管理页面检测到 `return` 参数时，在创建完成后跳转回去
- 或者使用 `sessionStorage` 存储返回地址

### 5. 多选面板的分类筛选

**决策**：支持传入 `allowedTypes` 参数，限制显示的素材类型和筛选标签

**理由**：
- 在作品详情页面，每个分类的"添加素材"按钮应该只显示对应类型的素材
- 简化用户选择，避免混淆
- 保持UI简洁

**实现**：
- `openMaterialMultiSelectDialog(allowedTypes, callback)`
- 如果 `allowedTypes` 只有一个类型，只显示该类型的筛选标签（或隐藏筛选标签）
- 如果 `allowedTypes` 包含多个类型，显示对应的筛选标签
- 如果 `allowedTypes` 为空或包含所有类型，显示所有筛选标签

