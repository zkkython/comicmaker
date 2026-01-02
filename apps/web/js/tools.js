/**
 * 工具页面逻辑 - 三栏布局版本
 */

// 工具定义
const TOOLS = [
    {
        id: 'generate_script',
        name: '生成剧本',
        description: '根据文本描述生成详细剧本文本',
        icon: '📝'
    },
    {
        id: 'generate_single_shot_storyboard',
        name: '生成单镜头分镜脚本',
        description: '根据剧本文本、预期时长和关联素材生成单镜头分镜脚本',
        icon: '🎬'
    },
    {
        id: 'generate_shot_prompts',
        name: '生成分镜提示词',
        description: '根据关联素材、分镜描述和预期时长生成5个提示词',
        icon: '📝'
    },
    {
        id: 'image_to_description',
        name: '图生描述',
        description: '根据图片生成描述文本',
        icon: '🖼️'
    },
    {
        id: 'image_to_style_description',
        name: '图生风格描述',
        description: '根据图片生成风格描述文本',
        icon: '🎨'
    },
    {
        id: 'text_to_image',
        name: '文生图',
        description: '根据文字描述生成图片',
        icon: '🎨'
    },
    {
        id: 'image_to_image',
        name: '图生图',
        description: '根据参考图片和文字描述生成图片',
        icon: '🖼️'
    },
    {
        id: 'vidu_ref_image_to_video',
        name: 'vidu参考生视频',
        description: '使用 vidu 模型根据参考图片和文字描述生成视频',
        icon: '🎞️'
    },
    {
        id: 'sora_image_to_video',
        name: 'sora生视频',
        description: '使用 sora 模型根据图片和文字描述生成视频',
        icon: '🎬'
    },
    {
        id: 'wan_image_to_video',
        name: 'wan图生视频',
        description: '使用 wan 模型根据图片和文字描述生成视频',
        icon: '🎥'
    },
    {
        id: 'keyframe_to_video',
        name: '首尾帧生视频',
        description: '根据首尾帧图片和文字描述生成视频',
        icon: '🎬'
    },
    {
        id: 'text_to_audio',
        name: '生音频',
        description: '根据文字描述生成音频',
        icon: '🔊'
    }
];

// 工具表单字段定义
const TOOL_FIELDS = {
    generate_script: [
        { name: 'description', label: '文本描述', type: 'textarea', required: true }
    ],
    generate_single_shot_storyboard: [
        { name: 'script', label: '剧本文本', type: 'textarea', required: true },
        { name: 'expected_duration', label: '预期时长（秒）', type: 'number', min: 1, max: 600, default: 60, required: true },
        { name: 'shot_duration', label: '单镜头预计时间（秒）', type: 'select', options: ['1', '2', '3', '4', '5', '6'], default: '5', required: true }
    ],
    image_to_description: [
        { name: 'image', label: '上传图片', type: 'file', accept: 'image/*', required: true },
        { name: 'material_type', label: '类型', type: 'select', options: ['人物', '场景', '道具', '其他'], required: true }
    ],
    image_to_style_description: [
        { name: 'image', label: '上传图片', type: 'file', accept: 'image/*', required: true },
        { name: 'description', label: '额外描述（可选）', type: 'textarea', required: false }
    ],
    text_to_image: [
        { name: 'prompt', label: '文字描述', type: 'textarea', required: true },
        { name: 'material_type', label: '类型', type: 'select', options: ['人物', '场景', '道具', '其他'], required: true },
        { name: 'model', label: '模型', type: 'select', options: ['seedream4.5', 'wan2.6', 'nanopro'], default: 'seedream4.5', required: true },
        { name: 'aspect_ratio', label: '比例', type: 'select', options: ['1:1', '3:4', '4:3', '16:9', '9:16'], default: '16:9', required: true },
        { name: 'resolution', label: '分辨率', type: 'select', options: ['1k', '2k'], default: '1k', required: true }
    ],
    image_to_image: [
        { name: 'prompt', label: '文字描述', type: 'textarea', required: true },
        { name: 'images', label: '上传图片（可多张）', type: 'file', accept: 'image/*', multiple: true, required: true },
        { name: 'model', label: '模型', type: 'select', options: ['seedream4.5', 'wan2.6', 'nanopro'], default: 'seedream4.5', required: true },
        { name: 'aspect_ratio', label: '比例', type: 'select', options: ['1:1', '3:4', '4:3', '16:9', '9:16'], default: '16:9', required: true },
        { name: 'resolution', label: '分辨率', type: 'select', options: ['1k', '2k'], default: '1k', required: true }
    ],
    vidu_ref_image_to_video: [
        { name: 'prompt', label: '文字描述', type: 'textarea', required: true },
        { name: 'images', label: '上传图片（最多7张）', type: 'file', accept: 'image/*', multiple: true, required: true },
        { name: 'aspect_ratio', label: '比例', type: 'select', options: ['1:1', '3:4', '4:3', '16:9', '9:16'], default: '16:9', required: true },
        { name: 'resolution', label: '分辨率', type: 'select', options: ['540p', '720p', '1080p'], default: '720p', required: true },
        { name: 'duration', label: '时长（秒）', type: 'select', options: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], default: '5', required: true }
    ],
    sora_image_to_video: [
        { name: 'prompt', label: '文字描述', type: 'textarea', required: true },
        { name: 'image', label: '上传图片', type: 'file', accept: 'image/*', required: true },
        { name: 'duration', label: '时长', type: 'select', options: ['4', '8', '12'], default: '4', required: true }
    ],
    wan_image_to_video: [
        { name: 'prompt', label: '文字描述', type: 'textarea', required: true },
        { name: 'image', label: '上传图片', type: 'file', accept: 'image/*', required: true },
        { name: 'model', label: '模型版本', type: 'select', options: ['wan2.5', 'wan2.6'], default: 'wan2.6', required: true },
        { name: 'resolution', label: '分辨率', type: 'select', options: ['480p', '720p', '1080p'], default: '720p', required: true },
        { name: 'duration', label: '时长（秒）', type: 'select', options: ['3', '4', '5', '6', '7', '8', '9', '10'], default: '5', required: true },
        { name: 'shot_type', label: '镜头类型', type: 'select', options: ['single', 'multi'], default: 'single', required: false },
        { name: 'enable_audio', label: '生成音频', type: 'checkbox', default: false }
    ],
    keyframe_to_video: [
        { name: 'start_frame', label: '首帧图片', type: 'file', accept: 'image/*', required: true },
        { name: 'end_frame', label: '尾帧图片', type: 'file', accept: 'image/*', required: true },
        { name: 'prompt', label: '文字描述', type: 'textarea', required: true },
        { name: 'aspect_ratio', label: '分辨率', type: 'select', options: ['9:16', '16:9', '4:3', '3:4'], required: true },
        { name: 'duration', label: '时长（秒）', type: 'number', min: 1, max: 60, required: true }
    ],
    text_to_audio: [
        { name: 'text', label: '文字描述', type: 'textarea', required: true },
        { name: 'duration', label: '时长（秒）', type: 'number', min: 1, max: 60, required: true }
    ],
    generate_shot_prompts: [
        { name: 'shot_description', label: '分镜描述', type: 'textarea', required: true },
        { name: 'duration', label: '预期时长（秒）', type: 'select', options: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'], default: '5', required: true }
    ]
};

let currentToolId = null;
let currentTaskId = null;
let currentTaskInput = null; // 保存当前任务的输入数据
let pollInterval = null;
let pollCount = 0;
let isPolling = false; // 标记是否正在轮询中，防止并发请求
const MAX_POLL_COUNT = 150; // 5分钟（150次 * 2秒）

// 初始化
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

// 渲染历史记录筛选下拉框
function renderHistoryFilter() {
    const filterSelect = document.getElementById('history-filter');
    if (!filterSelect) return;
    
    // 清空现有选项（保留"全部工具"）
    filterSelect.innerHTML = '<option value="">全部工具</option>';
    
    // 根据 TOOLS 数组生成选项
    TOOLS.forEach(tool => {
        if (tool.id && tool.name) {
            const option = document.createElement('option');
            option.value = tool.id;
            option.textContent = tool.name;
            filterSelect.appendChild(option);
        }
    });
}

// 渲染左侧工具列表
function renderToolsList() {
    const list = document.getElementById('tools-list');
    if (!list) return; // 如果元素不存在（如在 work-detail.html 中），直接返回
    list.innerHTML = TOOLS.map(tool => `
        <li>
            <div class="tool-item" onclick="selectTool('${tool.id}')">
                <span class="tool-icon">${tool.icon}</span>
                <span class="tool-name">${tool.name}</span>
            </div>
        </li>
    `).join('');
}

// 选择工具
function selectTool(toolId) {
    const tool = TOOLS.find(t => t.id === toolId);
    if (!tool) return;
    
    // 更新工具列表选中状态
    document.querySelectorAll('.tool-item').forEach(item => {
        item.classList.remove('active');
        if (item.querySelector('.tool-name').textContent === tool.name) {
            item.classList.add('active');
        }
    });
    
    // 更新编辑器标题
    document.getElementById('editor-title').textContent = tool.name;
    
    // 显示工具表单
    showToolForm(toolId);
    
    currentToolId = toolId;
}

// 显示工具表单
function showToolForm(toolId) {
    const tool = TOOLS.find(t => t.id === toolId);
    if (!tool) return;
    
    const fieldsContainer = document.getElementById('tool-form-fields');
    const fields = TOOL_FIELDS[toolId] || [];
    
    fieldsContainer.innerHTML = fields.map(field => {
        if (field.type === 'textarea') {
            return `
                <div class="form-group">
                    <label>${field.label}${field.required ? ' *' : ''}</label>
                    <textarea name="${field.name}" class="form-control" rows="5" ${field.required ? 'required' : ''}></textarea>
                </div>
            `;
        } else if (field.type === 'select') {
            return `
                <div class="form-group">
                    <label>${field.label}${field.required ? ' *' : ''}</label>
                    <select name="${field.name}" class="form-control" ${field.required ? 'required' : ''}>
                        ${field.default ? '' : '<option value="">请选择</option>'}
                        ${field.options.map(opt => `<option value="${opt}" ${field.default === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                </div>
            `;
        } else if (field.type === 'number') {
            return `
                <div class="form-group">
                    <label>${field.label}${field.required ? ' *' : ''}</label>
                    <input type="number" name="${field.name}" class="form-control" 
                           ${field.min ? `min="${field.min}"` : ''} 
                           ${field.max ? `max="${field.max}"` : ''} 
                           ${field.default !== undefined ? `value="${field.default}"` : ''} 
                           ${field.required ? 'required' : ''}>
                </div>
            `;
        } else if (field.type === 'file') {
            const fieldId = `tool-${field.name}-${Date.now()}`;
            const previewId = `tool-${field.name}-preview-${Date.now()}`;
            
            // 如果是图片上传字段，initImageUpload 会自动创建按钮组
            const isImageField = field.accept && field.accept.includes('image');
            
            return `
                <div class="form-group">
                    <label>${field.label}${field.required ? ' *' : ''}</label>
                    <div class="image-upload-wrapper" data-field-name="${field.name}" data-is-multiple="${field.multiple || false}">
                        <input type="file" id="${fieldId}" name="${field.name}" class="form-control" 
                               ${field.accept ? `accept="${field.accept}"` : ''} 
                               ${field.multiple ? 'multiple' : ''} 
                               ${field.required ? 'required' : ''}>
                    </div>
                    <div id="${previewId}" class="${field.multiple ? 'image-preview-grid' : 'image-preview'}"></div>
                </div>
            `;
        } else if (field.type === 'checkbox') {
            return `
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="${field.name}" class="form-control" 
                               ${field.default ? 'checked' : ''} 
                               ${field.required ? 'required' : ''}>
                        ${field.label}${field.required ? ' *' : ''}
                    </label>
                </div>
            `;
        }
    }).join('');
    
    // 对于 wan_image_to_video 工具，添加动态显示/隐藏 shot_type 字段的逻辑
    if (toolId === 'wan_image_to_video') {
        const modelSelect = fieldsContainer.querySelector('select[name="model"]');
        const shotTypeGroup = fieldsContainer.querySelector('select[name="shot_type"]')?.closest('.form-group');
        
        if (modelSelect && shotTypeGroup) {
            // 初始状态：根据默认值显示/隐藏
            const updateShotTypeVisibility = () => {
                if (modelSelect.value === 'wan2.6') {
                    shotTypeGroup.style.display = 'block';
                } else {
                    shotTypeGroup.style.display = 'none';
                }
            };
            
            // 监听模型选择变化
            modelSelect.addEventListener('change', updateShotTypeVisibility);
            
            // 初始化显示状态
            updateShotTypeVisibility();
        }
    }
    
    // 保存当前工具ID到表单
    document.getElementById('tool-form').dataset.toolId = toolId;
    
    // 初始化图片上传组件（为所有文件输入框）
    setTimeout(() => {
        const fileInputs = document.querySelectorAll('#tool-form input[type="file"]');
        fileInputs.forEach(input => {
            if (input.accept && input.accept.includes('image')) {
                const fieldName = input.name;
                const wrapper = input.closest('.image-upload-wrapper');
                const preview = wrapper ? wrapper.parentElement.querySelector('.image-preview, .image-preview-grid') : 
                                      input.closest('.form-group').querySelector('.image-preview, .image-preview-grid');
                const isMultiple = wrapper ? wrapper.dataset.isMultiple === 'true' : input.multiple;
                
                // 统一使用标准上传组件（选择文件、粘贴图片、选择素材）
                if (preview && !preview.id) {
                    preview.id = `tool-${fieldName}-preview`;
                }
                if (preview && preview.id) {
                    // 对于需要拖拽排序的多图片工具（image_to_image, vidu_ref_image_to_video），使用 initImageListUpload
                    if ((toolId === 'image_to_image' || toolId === 'vidu_ref_image_to_video') && isMultiple) {
                        // 创建图片列表容器
                        const listContainer = document.createElement('div');
                        listContainer.className = 'image-list-container';
                        listContainer.dataset.field = fieldName;
                        preview.appendChild(listContainer);
                        
                        // 初始化图片列表上传（支持拖拽排序和删除，会自动创建标准按钮组）
                        initImageListUpload(input, listContainer, toolId);
                    } else {
                        // 单图片或多图片（不需要拖拽排序），使用 initImageUpload
                        initImageUpload(input.id, preview.id, {
                            multiple: isMultiple,
                            onChange: (files) => {
                                // 文件变化时的处理
                            }
                        });
                        
                        // 在 initImageUpload 创建的按钮组中添加"选择素材"按钮
                        // initImageUpload 会将按钮组插入到 input 的父元素中
                        const container = input.parentElement;
                        const buttonGroup = container.querySelector('.image-upload-buttons');
                        if (buttonGroup) {
                            const selectMaterialBtn = document.createElement('button');
                            selectMaterialBtn.type = 'button';
                            selectMaterialBtn.className = 'btn btn-secondary btn-sm';
                            selectMaterialBtn.textContent = '选择素材';
                            selectMaterialBtn.onclick = () => openMaterialSelectDialog(fieldName, isMultiple);
                            buttonGroup.appendChild(selectMaterialBtn);
                        }
                    }
                }
            }
        });
    }, 0);
    
    // 对于生成分镜提示词工具，添加素材选择功能
    if (toolId === 'generate_shot_prompts') {
        // 添加素材选择区域
        const materialsSection = document.createElement('div');
        materialsSection.className = 'form-group';
        materialsSection.innerHTML = `
            <label>关联素材（可选）</label>
            <div class="materials-selection-section">
                <div class="material-type-section">
                    <div class="material-type-header">
                        <span>关联素材</span>
                        <button type="button" class="btn btn-sm btn-primary" onclick="addMaterialToShotPrompts()">添加素材</button>
                    </div>
                    <div id="shot-prompts-materials-list" class="storyboard-materials-list"></div>
                </div>
            </div>
        `;
        fieldsContainer.appendChild(materialsSection);
        
        // 初始化素材列表（空）
        if (!window.shotPromptsMaterials) {
            window.shotPromptsMaterials = [];
        }
        
        // 渲染素材列表
        renderShotPromptsMaterials();
    }
    
    // 对于生成单镜头分镜脚本工具，添加素材选择功能
    if (toolId === 'generate_single_shot_storyboard') {
        // 添加素材选择区域
        const materialsSection = document.createElement('div');
        materialsSection.className = 'form-group';
        materialsSection.innerHTML = `
            <label>关联素材（可选）</label>
            <div class="materials-selection-section">
                <div class="material-type-section">
                    <div class="material-type-header">
                        <span>人物素材</span>
                        <button type="button" class="btn btn-sm btn-primary" onclick="addMaterialToStoryboard('characters')">添加人物素材</button>
                    </div>
                    <div id="storyboard-character-materials-list" class="storyboard-materials-list"></div>
                </div>
                <div class="material-type-section">
                    <div class="material-type-header">
                        <span>场景素材</span>
                        <button type="button" class="btn btn-sm btn-primary" onclick="addMaterialToStoryboard('scenes')">添加场景素材</button>
                    </div>
                    <div id="storyboard-scene-materials-list" class="storyboard-materials-list"></div>
                </div>
                <div class="material-type-section">
                    <div class="material-type-header">
                        <span>道具素材</span>
                        <button type="button" class="btn btn-sm btn-primary" onclick="addMaterialToStoryboard('props')">添加道具素材</button>
                    </div>
                    <div id="storyboard-prop-materials-list" class="storyboard-materials-list"></div>
                </div>
            </div>
        `;
        fieldsContainer.appendChild(materialsSection);
        
        // 初始化素材列表（空）
        if (!window.storyboardMaterials) {
            window.storyboardMaterials = {
                characters: [],
                scenes: [],
                props: []
            };
        }
        
        // 渲染素材列表
        renderStoryboardMaterials();
    }
    
    // 显示表单，隐藏其他内容
    document.getElementById('tool-form').style.display = 'block';
    document.getElementById('task-status').style.display = 'none';
    document.getElementById('result-content').style.display = 'none';
    document.getElementById('editor-empty').style.display = 'none';
}

// 清空编辑器
function clearEditor() {
    document.getElementById('tool-form').reset();
    document.getElementById('tool-form').style.display = 'none';
    document.getElementById('task-status').style.display = 'none';
    document.getElementById('result-content').style.display = 'none';
    document.getElementById('editor-empty').style.display = 'block';
    document.getElementById('editor-title').textContent = '选择一个工具开始使用';
    
    // 清除选中状态
    document.querySelectorAll('.tool-item').forEach(item => {
        item.classList.remove('active');
    });
    
    currentToolId = null;
    stopPolling();
}

// 设置表单提交
function setupForm() {
    document.getElementById('tool-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const toolId = e.target.dataset.toolId;
        if (!toolId) return;
        
        const formData = new FormData(e.target);
        
        // 处理生成单镜头分镜脚本工具的素材列表
        if (toolId === 'generate_single_shot_storyboard') {
            // 获取素材名称列表
            const charMaterials = (window.storyboardMaterials?.characters || []).map(m => m.name);
            const sceneMaterials = (window.storyboardMaterials?.scenes || []).map(m => m.name);
            const propMaterials = (window.storyboardMaterials?.props || []).map(m => m.name);
            
            // 添加到 FormData
            formData.append('character_materials', JSON.stringify(charMaterials));
            formData.append('scene_materials', JSON.stringify(sceneMaterials));
            formData.append('prop_materials', JSON.stringify(propMaterials));
        }
        
        // 处理生成分镜提示词工具的素材列表
        if (toolId === 'generate_shot_prompts') {
            // 获取素材名称列表
            const relatedMaterials = (window.shotPromptsMaterials || []).map(m => m.name);
            
            // 添加到 FormData
            formData.append('related_materials', JSON.stringify(relatedMaterials));
            
            // 确保字段名正确（shot_description 和 duration）
            const shotDesc = formData.get('shot_description');
            if (shotDesc) {
                formData.set('shot_description', shotDesc);
            }
            const duration = formData.get('duration');
            if (duration) {
                formData.set('duration', duration);
            }
        }
        
        // 处理图生图和 vidu 参考生视频工具的多图片（使用 imageListData）
        if (toolId === 'image_to_image' || toolId === 'vidu_ref_image_to_video') {
            const imagesField = 'images';
            const imageList = imageListData[imagesField] || [];
            
            if (imageList.length === 0) {
                showAlertDialog('请选择图片', '错误');
                return;
            }
            
            // 限制 vidu 工具最多7张图片
            if (toolId === 'vidu_ref_image_to_video' && imageList.length > 7) {
                showAlertDialog('最多只能选择7张图片', '错误');
                return;
            }
            
            // 移除原有的 images 字段
            formData.delete(imagesField);
            // 按顺序添加图片（FastAPI 需要多次 append 同一个字段名来识别为列表）
            imageList.forEach((img, index) => {
                const fileName = img.file.name || `image_${index}.jpg`;
                formData.append(imagesField, img.file, fileName);
            });
        }
        
        try {
            // 创建任务
            const result = await API.createToolTask(toolId, formData);
            currentTaskId = result.task_id;
            
            // 保存表单数据（用于失败时显示）
            currentTaskInput = {
                tool_type: toolId,
                form_data: Object.fromEntries(formData.entries()),
                prompt: formData.get('prompt') || formData.get('description') || formData.get('script') || formData.get('text') || ''
            };
            
            // 显示任务状态
            showTaskStatus();
            
            // 开始轮询
            startPolling();
        } catch (error) {
            showAlertDialog('错误', `创建任务失败: ${error.message}`);
        }
    });
}

// 显示任务状态
function showTaskStatus() {
    // 保持表单显示，在表单下方显示任务状态
    document.getElementById('tool-form').style.display = 'block';
    document.getElementById('task-status').style.display = 'block';
    document.getElementById('result-content').style.display = 'none';
    document.getElementById('editor-empty').style.display = 'none';
    
    updateProgress(0, '正在处理...');
    // 隐藏查看详情按钮
    document.getElementById('task-status-actions').style.display = 'none';
}

// 更新进度
function updateProgress(progress, message) {
    document.getElementById('progress-fill').style.width = `${progress}%`;
    document.getElementById('progress-text').textContent = `${progress}%`;
    document.getElementById('task-status-message').textContent = message;
    
    // 如果是失败状态，显示查看详情按钮
    if (message === '任务失败') {
        document.getElementById('task-status-actions').style.display = 'block';
    }
    // 如果是正在处理状态，且有任务详情数据，显示查看详情按钮
    else if ((message === '正在处理...' || message.includes('正在处理')) && currentTaskInput) {
        // 检查是否有可显示的数据
        if (currentTaskInput.input || currentTaskInput.api_request || currentTaskInput.prompt) {
            document.getElementById('task-status-actions').style.display = 'block';
        }
    } else if (message !== '正在处理...' && !message.includes('正在处理')) {
        // 只有在非处理状态且没有数据时才隐藏
        if (!currentTaskInput || (!currentTaskInput.input && !currentTaskInput.api_request && !currentTaskInput.prompt)) {
            document.getElementById('task-status-actions').style.display = 'none';
        }
    }
}

// 开始轮询
function startPolling() {
    pollCount = 0;
    isPolling = false;
    
    // 使用递归 setTimeout 而不是 setInterval，这样可以更好地控制
    const poll = async () => {
        // 如果前一个请求还在进行中，跳过这次轮询
        if (isPolling) {
            pollInterval = setTimeout(poll, 2000);
            return;
        }
        
        pollCount++;
        
        if (pollCount > MAX_POLL_COUNT) {
            stopPolling();
            updateProgress(0, '任务超时');
            showAlertDialog('超时', '任务执行超时，请稍后重试');
            return;
        }
        
        // 检查是否还在轮询（可能在其他地方被停止了）
        if (!pollInterval) {
            return;
        }
        
        isPolling = true;
        
        try {
            const status = await API.getTaskStatus(currentTaskId);
            
            if (status.status === 'pending') {
                // 估算进度（简单线性估算）
                const estimatedProgress = Math.min(90, Math.floor((pollCount / MAX_POLL_COUNT) * 90));
                updateProgress(estimatedProgress, '正在处理...');
                
                // 更新任务的输入数据（如果API返回了）
                if (status.input || status.api_request || status.prompt) {
                    if (!currentTaskInput) {
                        currentTaskInput = {};
                    }
                    currentTaskInput.tool_type = status.tool_type || currentToolId;
                    if (status.input) {
                        currentTaskInput.input = status.input;
                    }
                    if (status.api_request) {
                        currentTaskInput.api_request = status.api_request;
                    }
                    if (status.prompt) {
                        currentTaskInput.prompt = status.prompt;
                    }
                    // 如果有任何任务详情数据，显示查看详情按钮
                    if (status.input || status.api_request || status.prompt) {
                        document.getElementById('task-status-actions').style.display = 'block';
                    }
                }
                
                // 继续轮询
                isPolling = false;
                pollInterval = setTimeout(poll, 2000);
            } else if (status.status === 'success') {
                stopPolling();
                updateProgress(100, '任务完成');
                
                // 延迟一下再显示结果，让用户看到完成状态
                setTimeout(async () => {
                    // 获取结果
                    const result = await API.getTaskResult(currentTaskId);
                    showResult(result);
                    
                    // 刷新历史记录
                    loadHistory(document.getElementById('history-filter').value);
                }, 500);
            } else if (status.status === 'failed') {
                stopPolling();
                updateProgress(0, '任务失败');
                // 失败时也保持表单显示
                document.getElementById('tool-form').style.display = 'block';
                
                // 保存任务的输入数据（如果API返回了）
                if (status.input) {
                    currentTaskInput = {
                        tool_type: status.tool_type || currentToolId,
                        input: status.input,
                        error: status.error
                    };
                } else if (currentTaskInput) {
                    // 如果没有从API获取到，使用之前保存的
                    currentTaskInput.error = status.error;
                }
                
                // 显示查看详情按钮
                document.getElementById('task-status-actions').style.display = 'block';
                
                showAlertDialog('失败', `任务执行失败: ${status.error || '未知错误'}`);
            }
        } catch (error) {
            console.error('轮询错误:', error);
            // 即使出错也继续轮询（可能是网络临时问题）
            isPolling = false;
            pollInterval = setTimeout(poll, 2000);
        } finally {
            // 确保在异常情况下也重置标志
            if (pollInterval) {
                // 如果还在轮询中，标志会在成功/失败分支中处理
            } else {
                isPolling = false;
            }
        }
    };
    
    // 开始第一次轮询
    pollInterval = setTimeout(poll, 2000);
}

// 停止轮询
function stopPolling() {
    if (pollInterval) {
        clearTimeout(pollInterval);
        pollInterval = null;
    }
    pollCount = 0;
    isPolling = false;
}

// 解析分镜提示词
function parseShotPrompts(text) {
    const lines = text.split('\n').map(l => l.trim()).filter(l => l);
    const result = {
        image_prompt: '',
        video_prompt: '',
        reference_video_prompt: '',
        audio_prompt: '',
        dialogue_prompt: ''
    };
    
    for (const line of lines) {
        if (line.startsWith('分镜图片提示词:')) {
            result.image_prompt = line.replace('分镜图片提示词:', '').trim();
        } else if (line.startsWith('分镜视频提示词:')) {
            result.video_prompt = line.replace('分镜视频提示词:', '').trim();
        } else if (line.startsWith('参考视频提示词:')) {
            result.reference_video_prompt = line.replace('参考视频提示词:', '').trim();
        } else if (line.startsWith('音频提示词:')) {
            result.audio_prompt = line.replace('音频提示词:', '').trim();
        } else if (line.startsWith('台词提示词:')) {
            result.dialogue_prompt = line.replace('台词提示词:', '').trim();
        } else {
            // 如果当前行不是新的提示词类型，可能是上一行的续行
            // 检查最后一个非空的提示词字段，追加内容
            if (result.image_prompt && !result.video_prompt && !line.includes(':')) {
                result.image_prompt += '\n' + line;
            } else if (result.video_prompt && !result.reference_video_prompt && !line.includes(':')) {
                result.video_prompt += '\n' + line;
            } else if (result.reference_video_prompt && !result.audio_prompt && !line.includes(':')) {
                result.reference_video_prompt += '\n' + line;
            } else if (result.audio_prompt && !result.dialogue_prompt && !line.includes(':')) {
                result.audio_prompt += '\n' + line;
            } else if (result.dialogue_prompt && !line.includes(':')) {
                result.dialogue_prompt += '\n' + line;
            }
        }
    }
    
    return result;
}

// 解析分镜脚本（全局函数，供其他页面使用）
window.parseStoryboard = function parseStoryboard(text) {
    const lines = text.split('\n').map(l => l.trim()).filter(l => l);
    const result = {
        related_materials: [],
        shots: []
    };
    
    // 解析第一行：剧本关联素材
    if (lines.length > 0 && lines[0].startsWith('剧本关联素材：')) {
        const materialsStr = lines[0].replace('剧本关联素材：', '').trim();
        result.related_materials = materialsStr.split('，').filter(m => m.trim());
    }
    
    // 解析分镜（每4行为一个分镜：分镜N、关联素材、时长、空行）
    let i = 1;
    while (i < lines.length) {
        const shotLine = lines[i];
        if (shotLine.match(/^分镜\d+:/)) {
            const shot = {
                number: shotLine.match(/^分镜(\d+):/)[1],
                description: shotLine.replace(/^分镜\d+:/, '').trim(),
                related_materials: [],
                duration: 0
            };
            
            // 下一行应该是关联素材
            if (i + 1 < lines.length && lines[i + 1].startsWith('关联素材:')) {
                const materialsStr = lines[i + 1].replace('关联素材:', '').trim();
                shot.related_materials = materialsStr.split('，').filter(m => m.trim());
                i++;
            }
            
            // 再下一行应该是时长
            if (i + 1 < lines.length && lines[i + 1].startsWith('时长:')) {
                const durationStr = lines[i + 1].replace('时长:', '').trim();
                shot.duration = parseInt(durationStr) || 0;
                i++;
            }
            
            result.shots.push(shot);
        }
        i++;
    }
    
    return result;
}

// 显示结果
function showResult(result) {
    const content = document.getElementById('result-content');
    const tool = TOOLS.find(t => t.id === result.tool_type);
    
    let html = `<h4>生成结果</h4>`;
    
    // 特殊处理：生成分镜提示词工具
    if (result.tool_type === 'generate_shot_prompts' && result.output.text) {
        try {
            const parsed = parseShotPrompts(result.output.text);
            
            // 显示5个提示词
            html += `<div class="shot-prompts-result">
                <div class="prompt-item">
                    <h5>分镜图片提示词：</h5>
                    <pre>${escapeHtml(parsed.image_prompt || '未解析到')}</pre>
                </div>
                <div class="prompt-item">
                    <h5>分镜视频提示词：</h5>
                    <pre>${escapeHtml(parsed.video_prompt || '未解析到')}</pre>
                </div>
                <div class="prompt-item">
                    <h5>参考视频提示词：</h5>
                    <pre>${escapeHtml(parsed.reference_video_prompt || '未解析到')}</pre>
                </div>
                <div class="prompt-item">
                    <h5>音频提示词：</h5>
                    <pre>${escapeHtml(parsed.audio_prompt || '未解析到')}</pre>
                </div>
                <div class="prompt-item">
                    <h5>台词提示词：</h5>
                    <pre>${escapeHtml(parsed.dialogue_prompt || '未解析到')}</pre>
                </div>
            </div>`;
        } catch (error) {
            console.error('解析分镜提示词失败:', error);
            html += `<div class="result-text"><pre>${escapeHtml(result.output.text)}</pre></div>`;
            html += `<div class="error-message">解析失败: ${error.message}</div>`;
        }
    }
    // 特殊处理：生成单镜头分镜脚本工具
    else if (result.tool_type === 'generate_single_shot_storyboard' && result.output.text) {
        try {
            const parsed = parseStoryboard(result.output.text);
            
            // 显示剧本关联素材
            if (parsed.related_materials.length > 0) {
                html += `<div class="storyboard-related-materials">
                    <h5>剧本关联素材：</h5>
                    <div class="materials-tags">
                        ${parsed.related_materials.map(m => `<span class="material-tag">${escapeHtml(m)}</span>`).join('')}
                    </div>
                </div>`;
            }
            
            // 显示分镜列表
            if (parsed.shots.length > 0) {
                html += `<div class="storyboard-shots">
                    <h5>分镜列表：</h5>
                    ${parsed.shots.map(shot => `
                        <div class="shot-item">
                            <div class="shot-header">
                                <span class="shot-number">分镜${shot.number}</span>
                                <span class="shot-duration">时长: ${shot.duration}秒</span>
                            </div>
                            <div class="shot-description">${escapeHtml(shot.description)}</div>
                            ${shot.related_materials.length > 0 ? `
                                <div class="shot-materials">
                                    关联素材: ${shot.related_materials.map(m => `<span class="material-tag">${escapeHtml(m)}</span>`).join('')}
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>`;
            } else {
                html += `<div class="result-text"><pre>${escapeHtml(result.output.text)}</pre></div>`;
            }
        } catch (error) {
            console.error('解析分镜脚本失败:', error);
            html += `<div class="result-text"><pre>${escapeHtml(result.output.text)}</pre></div>`;
            html += `<div class="error-message">解析失败: ${error.message}</div>`;
        }
    } else if (result.output.text) {
        // 文本结果
        html += `<div class="result-text"><pre>${escapeHtml(result.output.text)}</pre></div>`;
    } else if (result.output.image_path || result.output.url) {
        // 图片结果
        const url = result.output.url || result.output.image_path;
        html += `<div class="result-image"><img src="http://localhost:8000${url}" alt="生成结果"></div>`;
    } else if (result.output.video_url || result.output.video_path || result.output.url) {
        // 视频结果
        const videoUrl = result.output.video_url || result.output.video_path || result.output.url;
        // 如果是相对路径，转换为完整URL；如果是完整URL，直接使用
        const fullVideoUrl = videoUrl.startsWith('http') ? videoUrl : `http://localhost:8000${videoUrl}`;
        html += `<div class="result-video"><video controls src="${fullVideoUrl}"></video></div>`;
    } else if (result.output.audio_path || result.output.url) {
        // 音频结果
        const url = result.output.url || result.output.audio_path;
        html += `<div class="result-audio"><audio controls src="http://localhost:8000${url}"></audio></div>`;
    } else if (result.output.style_description) {
        // 风格描述结果（图生风格描述工具）
        html += `<div class="result-text"><h5>风格描述：</h5><pre>${escapeHtml(result.output.style_description)}</pre></div>`;
        // 同时显示完整的JSON数据
        html += `<div class="result-json"><h5>完整数据：</h5><pre>${JSON.stringify(result.output, null, 2)}</pre></div>`;
    } else if (result.output.description) {
        // 描述结果
        html += `<div class="result-text"><pre>${escapeHtml(result.output.description)}</pre></div>`;
    } else {
        html += `<div class="result-json"><pre>${JSON.stringify(result.output, null, 2)}</pre></div>`;
    }
    
    content.innerHTML = html;
    
    // 保持表单显示，在表单下方显示结果，隐藏状态
    document.getElementById('tool-form').style.display = 'block';
    document.getElementById('task-status').style.display = 'none';
    document.getElementById('result-content').style.display = 'block';
    document.getElementById('editor-empty').style.display = 'none';
}

// 加载历史记录
async function loadHistory(toolType = null) {
    try {
        const data = await API.listHistory(toolType);
        renderHistory(data.records);
    } catch (error) {
        console.error('加载历史记录失败:', error);
    }
}

// 渲染历史记录
function renderHistory(records) {
    const container = document.getElementById('history-list');
    
    if (records.length === 0) {
        container.innerHTML = '<div class="empty-state">暂无历史记录</div>';
        return;
    }
    
    container.innerHTML = records.map(record => {
        const tool = TOOLS.find(t => t.id === record.tool_type);
        const toolName = tool ? tool.name : record.tool_type;
        const date = new Date(record.created_at).toLocaleString('zh-CN');
        
        // 生成输入预览
        let inputPreview = '';
        let hasImage = false;
        let imagePaths = [];
        
        // 检查是否有图片输入
        if (record.input.image_path) {
            hasImage = true;
            imagePaths = [record.input.image_path];
        } else if (record.input.images && Array.isArray(record.input.images) && record.input.images.length > 0) {
            hasImage = true;
            imagePaths = record.input.images;
        } else if (record.input.image_paths && Array.isArray(record.input.image_paths) && record.input.image_paths.length > 0) {
            hasImage = true;
            imagePaths = record.input.image_paths;
        } else if (record.input.start_frame) {
            hasImage = true;
            imagePaths = [record.input.start_frame];
        } else if (record.input.end_frame) {
            hasImage = true;
            imagePaths = [record.input.end_frame];
        }
        
        // 使用全局的 convertPathToUrl 函数
        
        // 如果有图片，准备图片预览
        if (hasImage && imagePaths.length > 0) {
            // 生成所有图片的预览
            const imagePreviews = imagePaths.map(imagePath => {
                const imageUrl = convertPathToUrl(imagePath);
                return `<img src="${imageUrl}" alt="输入图片" class="history-input-image" onerror="this.style.display='none'">`;
            }).join('');
            
            // 如果有多张图片，使用容器包裹
            if (imagePaths.length > 1) {
                inputPreview = `<div class="history-input-images">${imagePreviews}</div>`;
            } else {
                inputPreview = imagePreviews;
            }
        } else {
            // 文字预览
            if (record.input.description) {
                inputPreview = escapeHtml(record.input.description.substring(0, 100));
                if (record.input.description.length > 100) inputPreview += '...';
            } else if (record.input.script) {
                inputPreview = escapeHtml(record.input.script.substring(0, 100));
                if (record.input.script.length > 100) inputPreview += '...';
            } else if (record.input.prompt) {
                inputPreview = escapeHtml(record.input.prompt.substring(0, 100));
                if (record.input.prompt.length > 100) inputPreview += '...';
            } else if (record.input.text) {
                inputPreview = escapeHtml(record.input.text.substring(0, 100));
                if (record.input.text.length > 100) inputPreview += '...';
            } else {
                const inputStr = JSON.stringify(record.input);
                inputPreview = escapeHtml(inputStr.substring(0, 100));
                if (inputStr.length > 100) inputPreview += '...';
            }
        }
        
        // 检查是否是文生图或图生图，并准备结果图片预览
        let outputImagePreview = '';
        const isImageGeneration = record.tool_type === 'text_to_image' || record.tool_type === 'image_to_image';
        if (isImageGeneration && (record.output.image_path || record.output.url)) {
            const outputImagePath = record.output.image_path || record.output.url;
            const outputImageUrl = convertPathToUrl(outputImagePath);
            outputImagePreview = `
                <div class="history-output-section">
                    <div class="history-output-label">生成结果：</div>
                    <img src="${outputImageUrl}" alt="生成结果" class="history-output-image" onerror="this.style.display='none'">
                </div>
            `;
        }
        
        // 检查是否是视频生成工具，并准备结果视频预览
        let outputVideoPreview = '';
        const isVideoGeneration = record.tool_type === 'vidu_ref_image_to_video' || 
                                   record.tool_type === 'sora_image_to_video' || 
                                   record.tool_type === 'wan_image_to_video';
        if (isVideoGeneration && (record.output.video_url || record.output.video_path || record.output.url)) {
            const videoUrl = record.output.video_url || record.output.video_path || record.output.url;
            // 如果是相对路径，转换为完整URL；如果是完整URL，直接使用
            const fullVideoUrl = videoUrl.startsWith('http') ? videoUrl : `http://localhost:8000${videoUrl}`;
            outputVideoPreview = `
                <div class="history-output-section">
                    <div class="history-output-label">生成结果：</div>
                    <video controls class="history-output-video" src="${fullVideoUrl}" onerror="this.style.display='none'"></video>
                </div>
            `;
        }
        
        return `
            <div class="history-item">
                <div class="history-item-header">
                    <h4>${toolName}</h4>
                    <span class="history-date">${date}</span>
                </div>
                <div class="history-item-content">
                    ${hasImage ? inputPreview : `<p class="history-input-preview">${inputPreview}</p>`}
                    ${outputImagePreview}
                    ${outputVideoPreview}
                </div>
                <div class="history-item-actions">
                    <button class="btn btn-sm btn-primary" onclick="viewHistoryDetail('${record.record_id}')">查看详情</button>
                    <button class="btn btn-sm btn-secondary" onclick="reuseHistory('${record.record_id}')">做同款</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteHistory('${record.record_id}')">删除</button>
                </div>
            </div>
        `;
    }).join('');
}

// 查看历史记录详情
async function viewHistoryDetail(recordId) {
    try {
        const record = await API.getHistoryDetail(recordId);
        const tool = TOOLS.find(t => t.id === record.tool_type);
        
        let html = `
            <h4>${tool ? tool.name : record.tool_type}</h4>
            <p><strong>生成时间：</strong>${new Date(record.created_at).toLocaleString('zh-CN')}</p>
            <h5>输入参数：</h5>
            <pre class="history-detail-json">${JSON.stringify(record.input, null, 2)}</pre>
        `;
        
        // 显示提示词（如果有）
        if (record.output.prompt) {
            html += `<h5>提示词：</h5>`;
            if (record.output.prompt.system_prompt) {
                html += `<div class="prompt-section">
                    <strong>系统提示词：</strong>
                    <pre class="history-detail-text history-detail-prompt">${escapeHtml(record.output.prompt.system_prompt)}</pre>
                </div>`;
            }
            if (record.output.prompt.user_message) {
                html += `<div class="prompt-section">
                    <strong>用户消息：</strong>
                    <pre class="history-detail-text history-detail-prompt">${escapeHtml(record.output.prompt.user_message)}</pre>
                </div>`;
            }
        }
        
        html += `<h5>输出结果：</h5>`;
        
        if (record.output.text) {
            html += `<pre class="history-detail-text">${escapeHtml(record.output.text)}</pre>`;
            // 如果有原始内容，显示完整内容
            if (record.output.raw_content && record.output.raw_content !== record.output.text) {
                html += `<h5>AI 返回的完整内容：</h5>`;
                html += `<pre class="history-detail-text history-detail-raw">${escapeHtml(record.output.raw_content)}</pre>`;
            }
        } else if (record.output.description) {
            html += `<pre class="history-detail-text">${escapeHtml(record.output.description)}</pre>`;
            // 如果有原始内容，显示完整内容
            if (record.output.raw_content && record.output.raw_content !== record.output.description) {
                html += `<h5>AI 返回的完整内容：</h5>`;
                html += `<pre class="history-detail-text history-detail-raw">${escapeHtml(record.output.raw_content)}</pre>`;
            }
        } else if (record.output.style_description) {
            html += `<pre class="history-detail-text">${escapeHtml(record.output.style_description)}</pre>`;
            // 如果有原始内容，显示完整内容
            if (record.output.raw_content && record.output.raw_content !== record.output.style_description) {
                html += `<h5>AI 返回的完整内容：</h5>`;
                html += `<pre class="history-detail-text history-detail-raw">${escapeHtml(record.output.raw_content)}</pre>`;
            }
        } else if (record.output.image_path || record.output.url) {
            const url = record.output.url || record.output.image_path;
            html += `<img src="http://localhost:8000${url}" alt="生成结果" class="history-detail-image">`;
        } else if (record.output.video_path || record.output.url) {
            const url = record.output.url || record.output.video_path;
            html += `<video controls src="http://localhost:8000${url}" class="history-detail-video"></video>`;
        } else if (record.output.audio_path || record.output.url) {
            const url = record.output.url || record.output.audio_path;
            html += `<audio controls src="http://localhost:8000${url}" class="history-detail-audio"></audio>`;
        } else {
            html += `<pre class="history-detail-json">${JSON.stringify(record.output, null, 2)}</pre>`;
        }
        
        // 如果有原始内容但还没有显示，单独显示
        if (record.output.raw_content && !html.includes('history-detail-raw')) {
            html += `<h5>AI 返回的完整内容：</h5>`;
            html += `<pre class="history-detail-text history-detail-raw">${escapeHtml(record.output.raw_content)}</pre>`;
        }
        
        // 显示AI接口的请求参数和响应JSON
        if (record.output.api_request || record.output.api_response) {
            html += `<h5>AI 接口请求参数：</h5>`;
            html += `<pre class="history-detail-json">${JSON.stringify(record.output.api_request || {}, null, 2)}</pre>`;
            html += `<h5>AI 接口响应JSON：</h5>`;
            html += `<pre class="history-detail-json">${JSON.stringify(record.output.api_response || {}, null, 2)}</pre>`;
        }
        
        // 在弹窗中显示详情
        document.getElementById('history-detail-content').innerHTML = html;
        document.getElementById('history-detail-dialog').showModal();
    } catch (error) {
        showAlertDialog('错误', `加载详情失败: ${error.message}`);
    }
}

// 关闭历史记录详情弹窗
function closeHistoryDetailDialog() {
    document.getElementById('history-detail-dialog').close();
}

// 删除历史记录
async function deleteHistory(recordId) {
    if (!await showConfirmDialog('确认删除', '确定要删除这条历史记录吗？')) {
        return;
    }
    
    try {
        await API.deleteHistory(recordId);
        loadHistory(document.getElementById('history-filter').value);
    } catch (error) {
        showAlertDialog('错误', `删除失败: ${error.message}`);
    }
}

// 做同款
async function reuseHistory(recordId) {
    try {
        const data = await API.reuseHistory(recordId);
        const toolId = data.tool_type;
        const input = data.input;
        
        // 选择工具
        selectTool(toolId);
        
        // 填充输入字段
        setTimeout(async () => {
            const form = document.getElementById('tool-form');
            Object.keys(input).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    if (field.type === 'file') {
                        // 文件字段无法预填充，跳过
                    } else {
                        field.value = input[key];
                    }
                }
            });
            
            // 处理图片输入字段
            // 1. 处理单图片输入（如 image_to_description）
            if (input.image_path || input.image) {
                const imagePath = input.image_path || input.image;
                const imageField = 'image';
                const imageInput = form.querySelector(`input[name="${imageField}"]`);
                
                if (imageInput && imagePath) {
                    try {
                        // 将路径转换为URL
                        const imageUrl = convertPathToUrl(imagePath);
                        
                        // 下载图片并转换为File对象
                        const response = await fetch(imageUrl);
                        const blob = await response.blob();
                        const fileName = imagePath.split('/').pop() || 'image.jpg';
                        const file = new File([blob], fileName, { type: blob.type });
                        
                        // 创建 DataTransfer 对象
                        const dataTransfer = new DataTransfer();
                        dataTransfer.items.add(file);
                        
                        // 设置文件列表
                        imageInput.files = dataTransfer.files;
                        
                        // 触发 change 事件，让 initImageUpload 处理预览
                        imageInput.dispatchEvent(new Event('change', { bubbles: true }));
                    } catch (error) {
                        console.error(`加载图片失败 ${imagePath}:`, error);
                    }
                }
            }
            
            // 2. 处理多图片输入（如 image_to_image, vidu_ref_image_to_video）
            if (toolId === 'image_to_image' || toolId === 'vidu_ref_image_to_video' || input.image_paths || (input.images && Array.isArray(input.images))) {
                const imagesField = 'images';
                const imagePaths = input.image_paths || input.images || [];
                
                if (imagePaths && imagePaths.length > 0) {
                    const imagesInput = form.querySelector(`input[name="${imagesField}"]`);
                    if (imagesInput) {
                        // 创建 DataTransfer 对象
                        const dataTransfer = new DataTransfer();
                        
                        // 加载每张图片
                        for (const imagePath of imagePaths) {
                            try {
                                // 将路径转换为URL
                                const imageUrl = convertPathToUrl(imagePath);
                                
                                // 下载图片并转换为File对象
                                const response = await fetch(imageUrl);
                                const blob = await response.blob();
                                const fileName = imagePath.split('/').pop() || 'image.jpg';
                                const file = new File([blob], fileName, { type: blob.type });
                                
                                // 添加到 DataTransfer
                                dataTransfer.items.add(file);
                            } catch (error) {
                                console.error(`加载图片失败 ${imagePath}:`, error);
                            }
                        }
                        
                        // 设置文件列表
                        imagesInput.files = dataTransfer.files;
                        
                        // 触发 change 事件，让 initImageUpload 处理预览
                        imagesInput.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            }
        }, 100);
    } catch (error) {
        showAlertDialog('错误', `加载输入参数失败: ${error.message}`);
    }
}

// 工具函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 将本地路径转换为URL的函数
function convertPathToUrl(imagePath) {
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
        return imagePath;
    } else if (imagePath.startsWith('/data/')) {
        // 已经是相对路径格式
        return `http://localhost:8000${imagePath}`;
    } else if (imagePath.includes('data/tools/')) {
        // 从绝对路径中提取 data/tools/ 之后的部分
        const idx = imagePath.indexOf('data/tools/');
        const relativePath = imagePath.substring(idx);
        return `http://localhost:8000/${relativePath}`;
    } else if (imagePath.includes('data/')) {
        // 从绝对路径中提取 data/ 之后的部分
        const idx = imagePath.indexOf('data/');
        const relativePath = imagePath.substring(idx);
        return `http://localhost:8000/${relativePath}`;
    } else {
        // 假设是相对路径，直接使用
        return `http://localhost:8000/data/tools/${imagePath}`;
    }
}

// 图片列表管理（用于图生图工具）
let imageListData = {}; // 存储每个字段的图片列表 { fieldName: [File, ...] }
let draggedImageElement = null; // 当前被拖拽的图片元素（全局变量）

function initImageListUpload(input, container, toolId = null) {
    const fieldName = input.name;
    imageListData[fieldName] = [];
    
    // 清空容器
    container.innerHTML = '';
    
    // 创建标准按钮组（选择文件、粘贴图片、选择素材）
    const buttonGroup = document.createElement('div');
    buttonGroup.className = 'image-upload-buttons';
    
    // 选择文件按钮
    const uploadBtn = document.createElement('button');
    uploadBtn.type = 'button';
    uploadBtn.className = 'btn btn-secondary btn-sm';
    uploadBtn.textContent = '选择文件';
    uploadBtn.onclick = () => input.click();
    
    // 粘贴图片按钮
    const pasteBtn = document.createElement('button');
    pasteBtn.type = 'button';
    pasteBtn.className = 'btn btn-secondary btn-sm';
    pasteBtn.textContent = '粘贴图片';
    pasteBtn.onclick = () => handlePasteImageForList(input, container, fieldName);
    
    // 选择素材按钮
    const selectMaterialBtn = document.createElement('button');
    selectMaterialBtn.type = 'button';
    selectMaterialBtn.className = 'btn btn-secondary btn-sm';
    selectMaterialBtn.textContent = '选择素材';
    selectMaterialBtn.onclick = () => openMaterialSelectDialog(fieldName, true);
    
    buttonGroup.appendChild(uploadBtn);
    buttonGroup.appendChild(pasteBtn);
    buttonGroup.appendChild(selectMaterialBtn);
    
    // 将按钮组插入到容器之前
    const wrapper = input.closest('.image-upload-wrapper');
    if (wrapper) {
        wrapper.insertBefore(buttonGroup, input);
    } else {
        input.parentElement.insertBefore(buttonGroup, input);
    }
    
    // 隐藏原始 input 并移除 required 属性（因为我们已经用 imageListData 来验证了）
    input.style.display = 'none';
    input.removeAttribute('required');
    
    // 文件选择处理
    input.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                addImageToList(fieldName, file, container);
            }
        });
        // 清空 input，允许重复选择同一文件
        input.value = '';
    });
    
    // 粘贴处理（全局监听）
    let pasteHandler = null;
    const activatePaste = () => {
        if (!pasteHandler) {
            pasteHandler = (e) => {
                // 检查是否在相关的输入框附近
                if (e.target === input || input.contains(e.target) || 
                    container.contains(e.target) || buttonGroup.contains(e.target) ||
                    wrapper?.contains(e.target)) {
                    handlePasteImageForList(input, container, fieldName, e);
                }
            };
            document.addEventListener('paste', pasteHandler);
        }
    };
    
    // 当输入框获得焦点时激活粘贴
    input.addEventListener('focus', activatePaste);
    buttonGroup.addEventListener('click', activatePaste);
    container.addEventListener('click', activatePaste);
    
    // 允许拖放文件到容器
    container.addEventListener('dragover', (e) => {
        e.preventDefault();
        container.classList.add('drag-over');
    });
    
    container.addEventListener('dragleave', (e) => {
        e.preventDefault();
        container.classList.remove('drag-over');
    });
    
    container.addEventListener('drop', (e) => {
        e.preventDefault();
        container.classList.remove('drag-over');
        const files = Array.from(e.dataTransfer.files);
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                addImageToList(fieldName, file, container);
            }
        });
    });
}

// 处理粘贴图片（用于图片列表）
async function handlePasteImageForList(input, container, fieldName, pasteEvent = null) {
    try {
        let files = [];
        
        if (pasteEvent) {
            // 使用粘贴事件的数据（推荐方式）
            const clipboardItems = pasteEvent.clipboardData?.items;
            if (clipboardItems) {
                const imageItems = Array.from(clipboardItems).filter(item => 
                    item.type.startsWith('image/')
                );
                
                for (const item of imageItems) {
                    const file = item.getAsFile();
                    if (file) {
                        files.push(file);
                    }
                }
            }
        } else {
            // 尝试使用新的 Clipboard API（需要用户授权）
            try {
                const clipboardData = await navigator.clipboard.read();
                for (const item of clipboardData) {
                    for (const type of item.types) {
                        if (type.startsWith('image/')) {
                            const blob = await item.getType(type);
                            const file = new File([blob], `pasted-image-${Date.now()}.${type.split('/')[1]}`, { type });
                            files.push(file);
                        }
                    }
                }
            } catch (clipboardError) {
                // 如果新 API 不可用或需要授权，提示用户使用 Ctrl+V
                if (typeof showAlertDialog === 'function') {
                    await showAlertDialog('请使用 Ctrl+V (Windows) 或 Cmd+V (Mac) 粘贴图片', '提示');
                } else {
                    alert('请使用 Ctrl+V (Windows) 或 Cmd+V (Mac) 粘贴图片');
                }
                return;
            }
        }
        
        if (files.length === 0) {
            if (typeof showAlertDialog === 'function') {
                await showAlertDialog('剪贴板中没有图片', '提示');
            } else {
                alert('剪贴板中没有图片');
            }
            return;
        }
        
        // 添加到图片列表
        files.forEach(file => {
            addImageToList(fieldName, file, container);
        });
        
    } catch (error) {
        console.error('粘贴图片失败:', error);
        if (typeof showAlertDialog === 'function') {
            await showAlertDialog('粘贴图片失败: ' + error.message, '错误');
        } else {
            alert('粘贴图片失败: ' + error.message);
        }
    }
}

function addImageToList(fieldName, file, container) {
    if (!imageListData[fieldName]) {
        imageListData[fieldName] = [];
    }
    
    const imageId = `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    imageListData[fieldName].push({ id: imageId, file: file });
    
    // 创建图片项
    const imageItem = document.createElement('div');
    imageItem.className = 'image-list-item';
    imageItem.draggable = true;
    imageItem.dataset.imageId = imageId;
    
    // 预览图片
    const reader = new FileReader();
    reader.onload = (e) => {
        imageItem.innerHTML = `
            <img src="${e.target.result}" alt="预览">
            <button type="button" class="image-list-remove" onclick="removeImageFromList('${fieldName}', '${imageId}')">×</button>
            <div class="image-list-drag-handle">⋮⋮</div>
        `;
        container.appendChild(imageItem);
        
        // 添加拖拽事件
        setupImageDrag(imageItem, fieldName);
    };
    reader.readAsDataURL(file);
}

function removeImageFromList(fieldName, imageId) {
    if (!imageListData[fieldName]) return;
    
    imageListData[fieldName] = imageListData[fieldName].filter(img => img.id !== imageId);
    
    // 查找包含该字段的容器
    const container = document.querySelector(`.image-list-container[data-field="${fieldName}"]`);
    if (!container) {
        // 如果找不到，尝试查找所有容器
        const allContainers = document.querySelectorAll('.image-list-container');
        for (const cont of allContainers) {
            const item = cont.querySelector(`[data-image-id="${imageId}"]`);
            if (item) {
                item.remove();
                return;
            }
        }
        return;
    }
    
    const item = container.querySelector(`[data-image-id="${imageId}"]`);
    if (item) {
        item.remove();
    }
}

function setupImageDrag(item, fieldName) {
    item.addEventListener('dragstart', (e) => {
        draggedImageElement = item;
        item.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', item.dataset.imageId); // 保存图片ID用于调试
    });
    
    item.addEventListener('dragend', (e) => {
        item.classList.remove('dragging');
        // 清除所有拖拽相关样式
        document.querySelectorAll('.image-list-item').forEach(el => {
            el.classList.remove('drag-over');
        });
        // 重置全局变量
        draggedImageElement = null;
    });
    
    item.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        // 只有当有被拖拽的元素且不是自己时才显示拖拽悬停效果
        if (draggedImageElement && draggedImageElement !== item) {
            item.classList.add('drag-over');
        }
    });
    
    item.addEventListener('dragleave', (e) => {
        // 只有当离开当前元素时才移除样式（避免子元素触发）
        if (!item.contains(e.relatedTarget)) {
            item.classList.remove('drag-over');
        }
    });
    
    item.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        item.classList.remove('drag-over');
        
        // 确保有被拖拽的元素且不是自己
        if (!draggedImageElement || draggedImageElement === item) {
            return;
        }
        
        const container = item.parentElement;
        if (!container) return;
        
        // 获取所有图片项（在DOM改变之前）
        const items = Array.from(container.querySelectorAll('.image-list-item'));
        const draggedIndex = items.indexOf(draggedImageElement);
        const targetIndex = items.indexOf(item);
        
        if (draggedIndex === -1 || targetIndex === -1 || draggedIndex === targetIndex) {
            return;
        }
        
        // 获取被拖拽元素的ID
        const draggedId = draggedImageElement.dataset.imageId;
        
        // 重新排序数据数组（在DOM改变之前）
        const data = imageListData[fieldName];
        if (data && data.length > 0) {
            const draggedDataIndex = data.findIndex(img => img.id === draggedId);
            
            if (draggedDataIndex !== -1) {
                // 从原位置移除
                const [moved] = data.splice(draggedDataIndex, 1);
                
                // 计算新的插入位置
                // 需要将DOM索引转换为数据数组索引
                // 由于数据数组和DOM顺序应该一致，可以直接使用targetIndex
                // 但如果向后移动（draggedDataIndex < targetIndex），移除后targetIndex需要减1
                // 如果向前移动（draggedDataIndex > targetIndex），targetIndex保持不变
                let insertIndex = targetIndex;
                if (draggedDataIndex < targetIndex) {
                    insertIndex = targetIndex - 1;
                }
                data.splice(insertIndex, 0, moved);
            }
        }
        
        // 重新排序 DOM（在数据数组更新之后）
        if (draggedIndex < targetIndex) {
            // 向后移动：插入到目标元素之后
            container.insertBefore(draggedImageElement, item.nextSibling);
        } else {
            // 向前移动：插入到目标元素之前
            container.insertBefore(draggedImageElement, item);
        }
    });
}

// 显示任务详情
function showTaskDetail() {
    if (!currentTaskInput) {
        showAlertDialog('提示', '暂无任务详情');
        return;
    }
    
    const dialog = document.getElementById('task-detail-dialog');
    const content = document.getElementById('task-detail-content');
    
    // 构建详情内容
    let html = '<div class="task-detail-section">';
    html += '<h4>工具类型</h4>';
    html += `<p>${currentTaskInput.tool_type || currentToolId || '未知'}</p>`;
    html += '</div>';
    
    // 显示提示词（优先显示保存的 prompt，否则从输入数据中提取）
    const prompt = currentTaskInput.prompt || 
                   (currentTaskInput.input && (currentTaskInput.input.prompt || currentTaskInput.input.description || currentTaskInput.input.script || currentTaskInput.input.text)) ||
                   (currentTaskInput.form_data && (currentTaskInput.form_data.prompt || currentTaskInput.form_data.description || currentTaskInput.form_data.script || currentTaskInput.form_data.text));
    
    if (prompt) {
        html += '<div class="task-detail-section">';
        html += '<h4>提示词</h4>';
        html += `<div class="task-detail-prompt">${escapeHtml(prompt)}</div>`;
        html += '</div>';
    }
    
    // 显示 AI 接口请求参数（如果有）
    if (currentTaskInput.api_request) {
        html += '<div class="task-detail-section">';
        html += '<h4>AI 接口请求参数</h4>';
        html += '<pre class="task-detail-json">' + escapeHtml(JSON.stringify(currentTaskInput.api_request, null, 2)) + '</pre>';
        html += '</div>';
    }
    
    // 显示输入参数
    html += '<div class="task-detail-section">';
    html += '<h4>输入参数</h4>';
    const inputData = currentTaskInput.input || currentTaskInput.form_data || {};
    // 过滤掉文件字段（无法序列化显示）
    const displayInputData = {};
    Object.keys(inputData).forEach(key => {
        if (inputData[key] instanceof File || inputData[key] instanceof FileList) {
            displayInputData[key] = `[文件: ${inputData[key].name || inputData[key].length + ' 个文件'}]`;
        } else {
            displayInputData[key] = inputData[key];
        }
    });
    html += '<pre class="task-detail-json">' + escapeHtml(JSON.stringify(displayInputData, null, 2)) + '</pre>';
    html += '</div>';
    
    // 显示错误信息（如果有）
    if (currentTaskInput.error) {
        html += '<div class="task-detail-section">';
        html += '<h4>错误信息</h4>';
        html += `<p class="task-detail-error">${escapeHtml(currentTaskInput.error)}</p>`;
        html += '</div>';
    }
    
    content.innerHTML = html;
    dialog.showModal();
}

// 关闭任务详情弹窗
function closeTaskDetailDialog() {
    const dialog = document.getElementById('task-detail-dialog');
    dialog.close();
}

// ========== 素材选择功能 ==========

let currentMaterialSelectField = null; // 当前选择素材的字段名
let currentMaterialSelectType = 'all'; // 当前筛选的素材类型
let currentMaterialSelectIsMultiple = false; // 当前选择素材的字段是否为多图片
let materialsList = []; // 当前加载的素材列表
let selectedMaterialId = null; // 选中的素材ID

// 打开素材选择面板
function openMaterialSelectDialog(fieldName, isMultiple = false) {
    currentMaterialSelectField = fieldName;
    currentMaterialSelectIsMultiple = isMultiple;
    selectedMaterialId = null;
    currentMaterialSelectType = 'all';
    
    // 重置筛选标签
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector('.filter-tab[data-type="all"]').classList.add('active');
    
    // 加载素材列表
    loadMaterialsForSelection('all');
    
    // 打开对话框
    const dialog = document.getElementById('material-select-dialog');
    dialog.showModal();
}

// 关闭素材选择面板
function closeMaterialSelectDialog() {
    const dialog = document.getElementById('material-select-dialog');
    dialog.close();
    currentMaterialSelectField = null;
    currentMaterialSelectIsMultiple = false;
    selectedMaterialId = null;
    materialsList = [];
}

// 筛选素材
function filterMaterials(type) {
    currentMaterialSelectType = type;
    selectedMaterialId = null;
    
    // 更新标签状态
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`.filter-tab[data-type="${type}"]`).classList.add('active');
    
    // 加载素材列表
    loadMaterialsForSelection(type);
}

// 加载素材列表
async function loadMaterialsForSelection(type) {
    try {
        const grid = document.getElementById('material-select-grid');
        grid.innerHTML = '<div style="text-align: center; padding: 2rem;">加载中...</div>';
        
        let allMaterials = [];
        
        if (type === 'all') {
            // 加载所有类型的素材
            const types = ['characters', 'scenes', 'props', 'others'];
            for (const materialType of types) {
                try {
                    const response = await API.listMaterials(materialType);
                    const materials = (response.materials || []).map(m => ({
                        ...m,
                        material_type: materialType
                    }));
                    allMaterials = allMaterials.concat(materials);
                } catch (error) {
                    console.error(`加载 ${materialType} 素材失败:`, error);
                }
            }
        } else {
            // 加载指定类型的素材
            const response = await API.listMaterials(type);
            allMaterials = (response.materials || []).map(m => ({
                ...m,
                material_type: type
            }));
        }
        
        materialsList = allMaterials;
        renderMaterialSelectGrid(allMaterials);
    } catch (error) {
        console.error('加载素材失败:', error);
        const grid = document.getElementById('material-select-grid');
        grid.innerHTML = '<div style="text-align: center; padding: 2rem; color: #e74c3c;">加载失败: ' + error.message + '</div>';
    }
}

// 渲染素材选择网格
function renderMaterialSelectGrid(materials) {
    const grid = document.getElementById('material-select-grid');
    
    if (materials.length === 0) {
        grid.innerHTML = '<div style="text-align: center; padding: 2rem; color: #7f8c8d;">暂无素材</div>';
        return;
    }
    
    grid.innerHTML = materials.map(material => {
        const hasMainImage = material.main_image && material.main_image.trim() !== '';
        const imageUrl = hasMainImage ? getMaterialImageUrl(material.main_image, material.material_type, material.id) : '';
        const isDisabled = !hasMainImage;
        // 如果素材被禁用，即使之前选中了，也不应该显示为选中状态
        const isSelected = !isDisabled && selectedMaterialId === material.id;
        
        return `
            <div class="material-grid-item-wrapper">
                <div class="material-grid-item ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}" 
                     ${isDisabled ? 'data-disabled="true"' : `onclick="selectMaterial('${material.id}')"`}
                     data-material-id="${material.id}"
                     data-has-image="${hasMainImage}">
                    <img src="${imageUrl || 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3E无图片%3C/text%3E%3C/svg%3E'}" 
                         alt="${material.name || ''}" 
                         onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3E无图片%3C/text%3E%3C/svg%3E'">
                    ${isDisabled ? '<div class="material-grid-item-disabled-overlay"><span>无主图</span></div>' : ''}
                    <div class="material-grid-item-overlay">
                        <button type="button" class="btn btn-sm btn-secondary" 
                                onclick="event.stopPropagation(); viewMaterialDetail('${material.id}')">详情</button>
                    </div>
                </div>
                <div class="material-grid-item-name">${escapeHtml(material.name || '未命名')}</div>
            </div>
        `;
    }).join('');
    
    // 如果当前选中的素材没有主图，清除选中状态
    if (selectedMaterialId) {
        const selectedMaterial = materialsList.find(m => m.id === selectedMaterialId);
        if (selectedMaterial && (!selectedMaterial.main_image || selectedMaterial.main_image.trim() === '')) {
            selectedMaterialId = null;
            // 同时清除UI上的选中状态
            document.querySelectorAll('.material-grid-item').forEach(item => {
                item.classList.remove('selected');
            });
        }
    }
}

// 获取素材图片URL（使用API端点以支持CORS）
function getMaterialImageUrl(imagePath, type, id) {
    if (!imagePath) return '';
    // 使用API端点而不是直接访问静态文件，以确保CORS头正确设置
    return `http://localhost:8000/api/materials/${type}/${id}/image/${imagePath}`;
}

// 选择素材
function selectMaterial(materialId) {
    // 先检查元素是否被禁用
    const materialItem = document.querySelector(`.material-grid-item[data-material-id="${materialId}"]`);
    if (materialItem && (materialItem.classList.contains('disabled') || materialItem.dataset.disabled === 'true')) {
        showAlertDialog('该素材没有主图，无法选择。请选择有主图的素材。', '提示');
        return; // 如果被禁用，直接返回，不进行任何操作
    }
    
    const material = materialsList.find(m => m.id === materialId);
    if (!material) return;
    
    // 检查是否有主图
    const hasMainImage = material.main_image && material.main_image.trim() !== '';
    if (!hasMainImage) {
        showAlertDialog('该素材没有主图，无法选择。请选择有主图的素材。', '提示');
        return;
    }
    
    selectedMaterialId = materialId;
    
    // 更新选中状态
    document.querySelectorAll('.material-grid-item').forEach(item => {
        item.classList.remove('selected');
    });
    if (materialItem) {
        materialItem.classList.add('selected');
    }
}

// 确认选择素材
async function confirmMaterialSelection() {
    if (!selectedMaterialId || !currentMaterialSelectField) {
        showAlertDialog('请先选择一个素材', '提示');
        return;
    }
    
    const material = materialsList.find(m => m.id === selectedMaterialId);
    if (!material) {
        showAlertDialog('素材不存在', '错误');
        selectedMaterialId = null; // 清除选中状态
        return;
    }
    
    // 检查是否有主图（优先检查，因为这是最关键的）
    const hasMainImage = material.main_image && material.main_image.trim() !== '';
    if (!hasMainImage) {
        showAlertDialog('该素材没有主图，无法选择。请选择有主图的素材。', '提示');
        selectedMaterialId = null; // 清除选中状态
        // 更新UI，移除选中状态
        document.querySelectorAll('.material-grid-item').forEach(item => {
            item.classList.remove('selected');
        });
        return;
    }
    
    // 检查元素是否被禁用（双重检查）
    const materialItem = document.querySelector(`.material-grid-item[data-material-id="${selectedMaterialId}"]`);
    if (materialItem && materialItem.classList.contains('disabled')) {
        showAlertDialog('该素材没有主图，无法选择。请选择有主图的素材。', '提示');
        selectedMaterialId = null; // 清除选中状态
        // 更新UI，移除选中状态
        document.querySelectorAll('.material-grid-item').forEach(item => {
            item.classList.remove('selected');
        });
        return;
    }
    
    try {
        // 再次检查是否有主图（防止状态不一致）
        const hasMainImage = material.main_image && material.main_image.trim() !== '';
        if (!hasMainImage) {
            showAlertDialog('该素材没有主图，无法选择。请选择有主图的素材。', '提示');
            selectedMaterialId = null;
            document.querySelectorAll('.material-grid-item').forEach(item => {
                item.classList.remove('selected');
            });
            return;
        }
        
        // 获取素材的主图URL
        const imageUrl = getMaterialImageUrl(material.main_image, material.material_type, material.id);
        if (!imageUrl || imageUrl.trim() === '') {
            showAlertDialog('该素材没有主图，无法选择。请选择有主图的素材。', '提示');
            selectedMaterialId = null;
            document.querySelectorAll('.material-grid-item').forEach(item => {
                item.classList.remove('selected');
            });
            return;
        }
        
        // 将图片URL转换为File对象
        let response;
        try {
            response = await fetch(imageUrl);
        } catch (fetchError) {
            // 处理网络错误（CORS、网络断开等）
            if (fetchError.name === 'TypeError' && fetchError.message.includes('Failed to fetch')) {
                throw new Error('无法获取图片，请检查图片路径是否正确或服务器是否可访问');
            }
            throw fetchError;
        }
        
        if (!response.ok) {
            throw new Error(`获取图片失败: ${response.status} ${response.statusText}`);
        }
        
        const blob = await response.blob();
        if (!blob || blob.size === 0) {
            throw new Error('图片文件为空或无效');
        }
        const file = new File([blob], material.main_image || 'material.jpg', { type: blob.type });
        
        // 获取文件输入框
        const input = document.querySelector(`input[name="${currentMaterialSelectField}"]`);
        if (!input) {
            showAlertDialog('找不到图片上传组件', '错误');
            return;
        }
        
        // 创建 DataTransfer 对象来设置文件
        const dataTransfer = new DataTransfer();
        
        if (currentMaterialSelectIsMultiple) {
            // 多图片组件（图生图工具）：添加到现有文件列表
            if (input.files) {
                Array.from(input.files).forEach(existingFile => {
                    dataTransfer.items.add(existingFile);
                });
            }
            dataTransfer.items.add(file);
        } else {
            // 单图片组件（图生描述工具等）：替换现有文件
            dataTransfer.items.add(file);
        }
        
        input.files = dataTransfer.files;
        
        // 触发 change 事件，让 initImageUpload 处理预览
        input.dispatchEvent(new Event('change', { bubbles: true }));
        
        // 关闭对话框
        closeMaterialSelectDialog();
    } catch (error) {
        console.error('添加素材失败:', error);
        showAlertDialog('添加素材失败: ' + error.message, '错误');
    }
}

// 查看素材详情
async function viewMaterialDetail(materialId) {
    const material = materialsList.find(m => m.id === materialId);
    if (!material) {
        showAlertDialog('素材不存在', '错误');
        return;
    }
    
    try {
        // 获取完整素材信息
        const fullMaterial = await API.getMaterial(material.material_type, materialId);
        
        const dialog = document.getElementById('material-detail-dialog');
        const content = document.getElementById('material-detail-content');
        
        // 使用原始的 material.material_type，因为 API 返回的 fullMaterial 不包含 material_type
        const imageUrl = getMaterialImageUrl(fullMaterial.main_image, material.material_type, fullMaterial.id);
        const hasImage = fullMaterial.main_image && fullMaterial.main_image.trim() !== '' && imageUrl;
        
        console.log('素材详情 - 图片URL:', imageUrl, 'hasImage:', hasImage);
        
        content.innerHTML = `
            <div class="material-detail-image">
                ${hasImage ? `<img src="${imageUrl}" alt="${escapeHtml(fullMaterial.name || '')}" onerror="console.error('图片加载失败:', '${imageUrl}'); this.onerror=null; this.parentElement.innerHTML='<div style=\\'width: 100%; height: 400px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #999;\\'>图片加载失败</div>';">` : '<div style="width: 100%; height: 400px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #999;">无图片</div>'}
            </div>
            <div class="material-detail-info">
                <h4>${escapeHtml(fullMaterial.name || '未命名')}</h4>
                <p>${escapeHtml(fullMaterial.description || '无描述')}</p>
            </div>
        `;
        
        dialog.showModal();
    } catch (error) {
        console.error('加载素材详情失败:', error);
        showAlertDialog('加载素材详情失败: ' + error.message, '错误');
    }
}

// 关闭素材详情面板
function closeMaterialDetailDialog() {
    const dialog = document.getElementById('material-detail-dialog');
    dialog.close();
}

// ========== 素材多选功能 ==========

let materialMultiSelectCallback = null; // 选择确认后的回调函数
let materialMultiSelectAllowedTypes = null; // 允许的素材类型
let materialMultiSelectSelectedIds = []; // 选中的素材ID数组
let materialMultiSelectMaterialsList = []; // 当前加载的素材列表
let materialMultiSelectCurrentType = 'all'; // 当前筛选的素材类型

// 打开素材多选面板
function openMaterialMultiSelectDialog(allowedTypes = null, callback = null) {
    materialMultiSelectCallback = callback;
    materialMultiSelectAllowedTypes = allowedTypes;
    materialMultiSelectSelectedIds = [];
    materialMultiSelectCurrentType = 'all';
    
    // 设置筛选标签
    const filterTabs = document.getElementById('material-multi-select-filter-tabs');
    if (allowedTypes && allowedTypes.length === 1) {
        // 只有一个类型，只显示该类型
        materialMultiSelectCurrentType = allowedTypes[0];
        filterTabs.innerHTML = `<button class="filter-tab active" data-type="${allowedTypes[0]}" onclick="filterMaterialsMultiSelect('${allowedTypes[0]}')">${getMaterialTypeName(allowedTypes[0])}</button>`;
    } else if (allowedTypes && allowedTypes.length > 1) {
        // 多个类型，显示对应的标签
        filterTabs.innerHTML = allowedTypes.map(type => 
            `<button class="filter-tab ${type === 'all' ? 'active' : ''}" data-type="${type}" onclick="filterMaterialsMultiSelect('${type}')">${getMaterialTypeName(type)}</button>`
        ).join('');
        materialMultiSelectCurrentType = 'all';
    } else {
        // 所有类型
        filterTabs.innerHTML = `
            <button class="filter-tab active" data-type="all" onclick="filterMaterialsMultiSelect('all')">全部</button>
            <button class="filter-tab" data-type="characters" onclick="filterMaterialsMultiSelect('characters')">人物</button>
            <button class="filter-tab" data-type="scenes" onclick="filterMaterialsMultiSelect('scenes')">场景</button>
            <button class="filter-tab" data-type="props" onclick="filterMaterialsMultiSelect('props')">道具</button>
            <button class="filter-tab" data-type="others" onclick="filterMaterialsMultiSelect('others')">其他</button>
        `;
        materialMultiSelectCurrentType = 'all';
    }
    
    // 更新选中计数
    updateMaterialMultiSelectCount();
    
    // 加载素材列表
    loadMaterialsForMultiSelect(materialMultiSelectCurrentType);
    
    // 打开对话框
    const dialog = document.getElementById('material-multi-select-dialog');
    dialog.showModal();
}

// 获取素材类型名称
function getMaterialTypeName(type) {
    const names = {
        'all': '全部',
        'characters': '人物',
        'scenes': '场景',
        'props': '道具',
        'others': '其他'
    };
    return names[type] || type;
}

// 关闭素材多选面板
function closeMaterialMultiSelectDialog() {
    const dialog = document.getElementById('material-multi-select-dialog');
    dialog.close();
    materialMultiSelectCallback = null;
    materialMultiSelectAllowedTypes = null;
    materialMultiSelectSelectedIds = [];
    materialMultiSelectMaterialsList = [];
    materialMultiSelectCurrentType = 'all';
}

// 筛选素材（多选）
function filterMaterialsMultiSelect(type) {
    materialMultiSelectCurrentType = type;
    
    // 更新标签状态
    document.querySelectorAll('#material-multi-select-filter-tabs .filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`#material-multi-select-filter-tabs .filter-tab[data-type="${type}"]`).classList.add('active');
    
    // 加载素材列表
    loadMaterialsForMultiSelect(type);
}

// 加载素材列表（多选）
async function loadMaterialsForMultiSelect(type) {
    try {
        const grid = document.getElementById('material-multi-select-grid');
        grid.innerHTML = '<div style="text-align: center; padding: 2rem;">加载中...</div>';
        
        let allMaterials = [];
        
        // 如果有限制类型，只加载允许的类型
        const typesToLoad = materialMultiSelectAllowedTypes || 
            (type === 'all' ? ['characters', 'scenes', 'props', 'others'] : [type]);
        
        if (type === 'all' && !materialMultiSelectAllowedTypes) {
            // 加载所有类型的素材
            const types = ['characters', 'scenes', 'props', 'others'];
            for (const materialType of types) {
                try {
                    const response = await API.listMaterials(materialType);
                    const materials = (response.materials || []).map(m => ({
                        ...m,
                        material_type: materialType
                    }));
                    allMaterials = allMaterials.concat(materials);
                } catch (error) {
                    console.error(`加载 ${materialType} 素材失败:`, error);
                }
            }
        } else {
            // 加载指定类型的素材
            const loadType = type === 'all' ? typesToLoad[0] : type;
            if (loadType && loadType !== 'all') {
                const response = await API.listMaterials(loadType);
                allMaterials = (response.materials || []).map(m => ({
                    ...m,
                    material_type: loadType
                }));
            }
        }
        
        materialMultiSelectMaterialsList = allMaterials;
        renderMaterialMultiSelectGrid(allMaterials);
    } catch (error) {
        console.error('加载素材失败:', error);
        const grid = document.getElementById('material-multi-select-grid');
        grid.innerHTML = '<div style="text-align: center; padding: 2rem; color: #e74c3c;">加载失败: ' + error.message + '</div>';
    }
}

// 渲染素材多选网格
function renderMaterialMultiSelectGrid(materials) {
    const grid = document.getElementById('material-multi-select-grid');
    
    if (materials.length === 0) {
        grid.innerHTML = '<div style="text-align: center; padding: 2rem; color: #7f8c8d;">暂无素材</div>';
        return;
    }
    
    grid.innerHTML = materials.map(material => {
        const hasMainImage = material.main_image && material.main_image.trim() !== '';
        const imageUrl = hasMainImage ? getMaterialImageUrl(material.main_image, material.material_type, material.id) : '';
        const isDisabled = !hasMainImage;
        const isSelected = !isDisabled && materialMultiSelectSelectedIds.includes(material.id);
        
        return `
            <div class="material-grid-item-wrapper">
                <div class="material-grid-item ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}" 
                     ${isDisabled ? 'data-disabled="true"' : `onclick="toggleMaterialMultiSelect('${material.id}')"`}
                     data-material-id="${material.id}"
                     data-has-image="${hasMainImage}">
                    ${isSelected ? '<div class="material-multi-select-checkmark">✓</div>' : ''}
                    <img src="${imageUrl || 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3E无图片%3C/text%3E%3C/svg%3E'}" 
                         alt="${material.name || ''}" 
                         onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3E无图片%3C/text%3E%3C/svg%3E'">
                    ${isDisabled ? '<div class="material-grid-item-disabled-overlay"><span>无主图</span></div>' : ''}
                    <div class="material-grid-item-overlay">
                        <button type="button" class="btn btn-sm btn-secondary" 
                                onclick="event.stopPropagation(); viewMaterialDetail('${material.id}')">详情</button>
                    </div>
                </div>
                <div class="material-grid-item-name">${escapeHtml(material.name || '未命名')}</div>
            </div>
        `;
    }).join('');
    
    updateMaterialMultiSelectCount();
}

// 切换素材选中状态（多选）
function toggleMaterialMultiSelect(materialId) {
    const materialItem = document.querySelector(`#material-multi-select-grid .material-grid-item[data-material-id="${materialId}"]`);
    if (materialItem && (materialItem.classList.contains('disabled') || materialItem.dataset.disabled === 'true')) {
        showAlertDialog('该素材没有主图，无法选择。请选择有主图的素材。', '提示');
        return;
    }
    
    const material = materialMultiSelectMaterialsList.find(m => m.id === materialId);
    if (!material) return;
    
    const hasMainImage = material.main_image && material.main_image.trim() !== '';
    if (!hasMainImage) {
        showAlertDialog('该素材没有主图，无法选择。请选择有主图的素材。', '提示');
        return;
    }
    
    // 切换选中状态
    const index = materialMultiSelectSelectedIds.indexOf(materialId);
    if (index > -1) {
        materialMultiSelectSelectedIds.splice(index, 1);
        materialItem.classList.remove('selected');
        // 移除勾号
        const checkmark = materialItem.querySelector('.material-multi-select-checkmark');
        if (checkmark) checkmark.remove();
    } else {
        materialMultiSelectSelectedIds.push(materialId);
        materialItem.classList.add('selected');
        // 添加勾号
        if (!materialItem.querySelector('.material-multi-select-checkmark')) {
            const checkmark = document.createElement('div');
            checkmark.className = 'material-multi-select-checkmark';
            checkmark.textContent = '✓';
            materialItem.appendChild(checkmark);
        }
    }
    
    updateMaterialMultiSelectCount();
}

// 更新选中计数
function updateMaterialMultiSelectCount() {
    const countEl = document.getElementById('material-multi-select-count');
    if (countEl) {
        countEl.textContent = `已选择 ${materialMultiSelectSelectedIds.length} 个素材`;
    }
}

// 刷新素材列表（多选）
function refreshMaterialMultiSelect() {
    loadMaterialsForMultiSelect(materialMultiSelectCurrentType);
}

// 创建素材（从多选面板）
function createMaterialFromMultiSelect() {
    const returnUrl = window.location.href;
    const type = materialMultiSelectCurrentType !== 'all' ? materialMultiSelectCurrentType : 
                 (materialMultiSelectAllowedTypes && materialMultiSelectAllowedTypes.length === 1 ? materialMultiSelectAllowedTypes[0] : null);
    let url = 'materials.html';
    if (type) {
        url += `?type=${type}`;
    }
    url += `&return=${encodeURIComponent(returnUrl)}`;
    window.location.href = url;
}

// 确认选择素材（多选）
function confirmMaterialMultiSelection() {
    if (materialMultiSelectSelectedIds.length === 0) {
        showAlertDialog('请至少选择一个素材', '提示');
        return;
    }
    
    // 过滤掉没有主图的素材
    const validIds = materialMultiSelectSelectedIds.filter(id => {
        const material = materialMultiSelectMaterialsList.find(m => m.id === id);
        return material && material.main_image && material.main_image.trim() !== '';
    });
    
    if (validIds.length === 0) {
        showAlertDialog('选中的素材都没有主图，无法使用', '提示');
        return;
    }
    
    // 调用回调函数
    if (materialMultiSelectCallback) {
        materialMultiSelectCallback(validIds);
    }
    
    // 关闭对话框
    closeMaterialMultiSelectDialog();
}

// ========== 生成单镜头分镜脚本工具的素材选择功能 ==========

// 全局变量：存储分镜脚本工具的素材列表
window.storyboardMaterials = window.storyboardMaterials || {
    characters: [],
    scenes: [],
    props: []
};

// 添加素材到分镜脚本工具
function addMaterialToStoryboard(type) {
    // 映射类型名称
    const typeMap = {
        'characters': 'characters',
        'scenes': 'scenes',
        'props': 'props'
    };
    
    const materialType = typeMap[type];
    if (!materialType) return;
    
    // 打开素材多选面板，只显示对应类型的素材
    openMaterialMultiSelectDialog([materialType], async (selectedIds) => {
        // 去重：只添加不存在的素材
        const currentIds = window.storyboardMaterials[materialType] || [];
        const newIds = selectedIds.filter(id => !currentIds.includes(id));
        
        if (newIds.length === 0) {
            await showAlertDialog('所选素材已存在', '提示');
            return;
        }
        
        // 获取素材详情并添加到列表
        try {
            for (const materialId of newIds) {
                const material = await API.getMaterial(materialType, materialId);
                window.storyboardMaterials[materialType].push({
                    id: materialId,
                    name: material.name,
                    material_type: materialType
                });
            }
            
            // 重新渲染素材列表
            renderStoryboardMaterials();
        } catch (error) {
            console.error('加载素材详情失败:', error);
            await showAlertDialog('加载素材详情失败: ' + error.message, '错误');
        }
    });
}

// 从分镜脚本工具移除素材
function removeMaterialFromStoryboard(type, materialId) {
    const materialType = type === 'characters' ? 'characters' : type === 'scenes' ? 'scenes' : 'props';
    window.storyboardMaterials[materialType] = window.storyboardMaterials[materialType].filter(
        m => m.id !== materialId
    );
    renderStoryboardMaterials();
}

// ========== 生成分镜提示词工具的素材选择功能 ==========

// 全局变量：存储分镜提示词工具的素材列表
window.shotPromptsMaterials = window.shotPromptsMaterials || [];

// 添加素材到分镜提示词工具
function addMaterialToShotPrompts() {
    // 打开素材多选面板，显示所有类型的素材
    openMaterialMultiSelectDialog(null, async (selectedIds) => {
        // 去重：只添加不存在的素材
        const currentIds = window.shotPromptsMaterials.map(m => m.id);
        const newIds = selectedIds.filter(id => !currentIds.includes(id));
        
        if (newIds.length === 0) {
            await showAlertDialog('所选素材已存在', '提示');
            return;
        }
        
        // 获取素材详情并添加到列表
        try {
            for (const materialId of newIds) {
                // 需要确定素材类型，先尝试所有类型
                let material = null;
                let materialType = null;
                
                for (const type of ['characters', 'scenes', 'props', 'others']) {
                    try {
                        material = await API.getMaterial(type, materialId);
                        if (material) {
                            materialType = type;
                            break;
                        }
                    } catch (error) {
                        continue;
                    }
                }
                
                if (material && material.name) {
                    window.shotPromptsMaterials.push({
                        id: materialId,
                        name: material.name,
                        material_type: materialType
                    });
                }
            }
            
            // 重新渲染素材列表
            renderShotPromptsMaterials();
        } catch (error) {
            console.error('加载素材详情失败:', error);
            await showAlertDialog('加载素材详情失败: ' + error.message, '错误');
        }
    });
}

// 从分镜提示词工具移除素材
function removeMaterialFromShotPrompts(materialId) {
    window.shotPromptsMaterials = window.shotPromptsMaterials.filter(
        m => m.id !== materialId
    );
    renderShotPromptsMaterials();
}

// 渲染分镜提示词工具的素材列表
async function renderShotPromptsMaterials() {
    const listEl = document.getElementById('shot-prompts-materials-list');
    if (!listEl) return;
    
    const materials = window.shotPromptsMaterials || [];
    
    if (materials.length === 0) {
        listEl.innerHTML = '<div style="color: #999; padding: 0.5rem;">暂无素材</div>';
        return;
    }
    
    listEl.innerHTML = materials.map(material => {
        const imageUrl = `http://localhost:8000/api/materials/${material.material_type}/${material.id}/image/main.jpg`;
        return `
            <div class="storyboard-material-item" data-material-id="${material.id}">
                <img src="${imageUrl}" alt="${material.name}" onerror="this.style.display='none'">
                <span>${material.name}</span>
                <button type="button" class="btn btn-sm btn-danger" onclick="removeMaterialFromShotPrompts('${material.id}')">删除</button>
            </div>
        `;
    }).join('');
}

// 渲染分镜脚本工具的素材列表
async function renderStoryboardMaterials() {
    const types = ['characters', 'scenes', 'props'];
    const typeNames = { characters: '人物', scenes: '场景', props: '道具' };
    const typeIds = { characters: 'storyboard-character', scenes: 'storyboard-scene', props: 'storyboard-prop' };
    
    for (const type of types) {
        const listEl = document.getElementById(`${typeIds[type]}-materials-list`);
        if (!listEl) continue;
        
        const materials = window.storyboardMaterials[type] || [];
        
        if (materials.length === 0) {
            listEl.innerHTML = '<div style="color: #999; padding: 0.5rem;">暂无素材</div>';
            continue;
        }
        
        listEl.innerHTML = materials.map(material => {
            const imageUrl = `http://localhost:8000/api/materials/${type}/${material.id}/image/main.jpg`;
            return `
                <div class="storyboard-material-item" data-material-id="${material.id}">
                    <img src="${imageUrl}" alt="${material.name}" onerror="this.style.display='none'">
                    <span>${material.name}</span>
                    <button type="button" class="btn btn-sm btn-danger" onclick="removeMaterialFromStoryboard('${type}', '${material.id}')">删除</button>
                </div>
            `;
        }).join('');
    }
}
