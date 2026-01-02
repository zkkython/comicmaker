/**
 * 风格管理页面脚本
 */

let currentStyle = null;
let imageCacheTimestamp = Date.now(); // 用于强制刷新图片

document.addEventListener('DOMContentLoaded', () => {
    // 创建按钮
    document.getElementById('create-btn').addEventListener('click', () => {
        openModal();
    });
    
    // 初始化图片上传组件
    initImageUpload('reference-image', 'reference-image-preview', {
        onChange: (files) => {
            if (files.length > 0) {
                // 显示"生成风格描述"按钮
                document.getElementById('generate-description-btn').style.display = 'block';
            } else {
                document.getElementById('generate-description-btn').style.display = 'none';
            }
        }
    });
    
    // 在图片上传按钮组中添加"选择素材"按钮
    setTimeout(() => {
        const imageInput = document.getElementById('reference-image');
        if (imageInput) {
            const container = imageInput.parentElement;
            const buttonGroup = container.querySelector('.image-upload-buttons');
            if (buttonGroup) {
                // 检查是否已经添加过"选择素材"按钮
                if (!buttonGroup.querySelector('.select-material-btn')) {
                    const selectMaterialBtn = document.createElement('button');
                    selectMaterialBtn.type = 'button';
                    selectMaterialBtn.className = 'btn btn-secondary btn-sm select-material-btn';
                    selectMaterialBtn.textContent = '选择素材';
                    selectMaterialBtn.onclick = () => openMaterialSelectDialog('reference-image', false);
                    buttonGroup.appendChild(selectMaterialBtn);
                }
            }
        }
    }, 100);
    
    // 生成风格描述按钮
    document.getElementById('generate-description-btn').addEventListener('click', async () => {
        await generateStyleDescription();
    });
    
    // 关闭模态框
    document.getElementById('close-modal').addEventListener('click', closeModal);
    document.getElementById('cancel-btn').addEventListener('click', closeModal);

    // 表单提交
    document.getElementById('style-form').addEventListener('submit', handleSubmit);

    // 初始加载
    loadStyles();
});

async function loadStyles() {
    try {
        // 更新图片缓存时间戳，强制刷新图片
        imageCacheTimestamp = Date.now();
        const styles = await API.getStyles();
        renderStyles(styles);
    } catch (error) {
        console.error('加载风格失败:', error);
        await showAlertDialog('加载风格失败: ' + error.message, '错误');
    }
}

function renderStyles(styles) {
    const listEl = document.getElementById('styles-list');
    
    if (styles.length === 0) {
        listEl.innerHTML = '<p style="text-align: center; color: #7f8c8d;">暂无风格，点击"创建新风格"开始创建</p>';
        return;
    }

    listEl.innerHTML = styles.map(style => `
        <div class="style-card">
            ${style.reference_image ? `
                <img src="${getImageUrl(style.reference_image, style.id)}" 
                     alt="${style.name}" 
                     class="style-card-image"
                     onerror="this.style.display='none'">
            ` : `
                <div class="style-card-image style-card-image-placeholder">无图片</div>
            `}
            <div class="style-card-content">
                <div class="style-card-title">${style.name}</div>
                <div class="style-card-description">${style.description || ''}</div>
                <div class="style-card-actions">
                    <button class="btn btn-primary" onclick="editStyle('${style.id}')">编辑</button>
                    <button class="btn btn-danger" onclick="deleteStyle('${style.id}')">删除</button>
                </div>
            </div>
        </div>
    `).join('');
}

function getImageUrl(imagePath, id) {
    if (!imagePath) return '';
    // 使用 API 端点，并添加时间戳避免缓存
    return `http://localhost:8000/api/styles/${id}/image/${imagePath}?t=${imageCacheTimestamp}`;
}

function openModal(style = null) {
    currentStyle = style;
    const modal = document.getElementById('style-modal');
    const form = document.getElementById('style-form');
    
    document.getElementById('modal-title').textContent = style ? '编辑风格' : '创建新风格';
    
    if (style) {
        document.getElementById('style-id').value = style.id;
        document.getElementById('style-name').value = style.name || '';
        document.getElementById('style-description').value = style.description || '';
        
        // 显示现有图片预览
        if (style.reference_image) {
            document.getElementById('reference-image-preview').innerHTML = 
                `<img src="${getImageUrl(style.reference_image, style.id)}" alt="参考图片">`;
            document.getElementById('generate-description-btn').style.display = 'block';
        } else {
            document.getElementById('reference-image-preview').innerHTML = '';
            document.getElementById('generate-description-btn').style.display = 'none';
        }
    } else {
        form.reset();
        document.getElementById('reference-image-preview').innerHTML = '';
        document.getElementById('generate-description-btn').style.display = 'none';
    }
    
    modal.showModal();
}

function closeModal() {
    const modal = document.getElementById('style-modal');
    modal.close();
    currentStyle = null;
}

async function generateStyleDescription() {
    const imageInput = document.getElementById('reference-image');
    if (!imageInput.files || imageInput.files.length === 0) {
        await showAlertDialog('请先上传参考图片', '提示');
        return;
    }
    
    try {
        // 显示加载状态
        const btn = document.getElementById('generate-description-btn');
        const originalText = btn.textContent;
        btn.textContent = '生成中...';
        btn.disabled = true;
        
        // 创建 FormData 并提交到图生风格描述工具
        const formData = new FormData();
        formData.append('tool_type', 'image_to_style_description');
        formData.append('image', imageInput.files[0]);
        
        // 调用工具 API
        const result = await API.createToolTask('image_to_style_description', formData);
        const taskId = result.task_id;
        
        // 轮询任务状态
        let attempts = 0;
        const maxAttempts = 60; // 最多轮询60次（约1分钟）
        
        const pollInterval = setInterval(async () => {
            attempts++;
            try {
                const status = await API.getTaskStatus(taskId);
                
                if (status.status === 'success') {
                    clearInterval(pollInterval);
                    // 获取任务结果（包含输出数据）
                    const result = await API.getTaskResult(taskId);
                    const styleDescription = result.output?.style_description || result.output?.raw_content || '';
                    
                    if (styleDescription) {
                        // 填充到描述字段
                        document.getElementById('style-description').value = styleDescription;
                        btn.textContent = originalText;
                        btn.disabled = false;
                        await showAlertDialog('风格描述生成成功', '成功');
                    } else {
                        btn.textContent = originalText;
                        btn.disabled = false;
                        await showAlertDialog('生成失败: 未获取到风格描述', '错误');
                    }
                } else if (status.status === 'failed') {
                    clearInterval(pollInterval);
                    btn.textContent = originalText;
                    btn.disabled = false;
                    await showAlertDialog('生成失败: ' + (status.error || '未知错误'), '错误');
                } else if (attempts >= maxAttempts) {
                    clearInterval(pollInterval);
                    btn.textContent = originalText;
                    btn.disabled = false;
                    await showAlertDialog('生成超时，请稍后重试', '提示');
                }
            } catch (error) {
                clearInterval(pollInterval);
                btn.textContent = originalText;
                btn.disabled = false;
                await showAlertDialog('生成失败: ' + error.message, '错误');
            }
        }, 1000);
    } catch (error) {
        await showAlertDialog('生成失败: ' + error.message, '错误');
    }
}

async function handleSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('name', document.getElementById('style-name').value);
    formData.append('description', document.getElementById('style-description').value);
    
    const referenceImage = document.getElementById('reference-image').files[0];
    if (referenceImage) {
        formData.append('reference_image', referenceImage);
    }
    
    try {
        const styleId = document.getElementById('style-id').value;
        if (styleId) {
            await API.updateStyle(styleId, formData);
        } else {
            await API.createStyle(formData);
        }
        
        closeModal();
        loadStyles();
        await showAlertDialog('保存成功', '成功');
    } catch (error) {
        console.error('保存风格失败:', error);
        await showAlertDialog('保存失败: ' + error.message, '错误');
    }
}

async function editStyle(styleId) {
    try {
        const style = await API.getStyle(styleId);
        openModal(style);
    } catch (error) {
        console.error('加载风格失败:', error);
        await showAlertDialog('加载风格失败: ' + error.message, '错误');
    }
}

async function deleteStyle(styleId) {
    if (!await showConfirmDialog('确认删除', '确定要删除这个风格吗？')) {
        return;
    }
    
    try {
        await API.deleteStyle(styleId);
        loadStyles();
        await showAlertDialog('删除成功', '成功');
    } catch (error) {
        console.error('删除风格失败:', error);
        await showAlertDialog('删除失败: ' + error.message, '错误');
    }
}

