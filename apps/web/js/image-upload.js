/**
 * 图片上传工具函数
 * 支持文件上传、剪贴板粘贴和图片预览
 */

/**
 * 初始化图片上传组件
 * @param {string} inputId - 文件输入框的ID
 * @param {string} previewId - 预览容器的ID
 * @param {Object} options - 配置选项
 * @param {boolean} options.multiple - 是否支持多文件
 * @param {Function} options.onChange - 文件变化回调
 */
function initImageUpload(inputId, previewId, options = {}) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    
    if (!input || !preview) {
        console.warn(`图片上传组件初始化失败: ${inputId} 或 ${previewId} 不存在`);
        return;
    }
    
    const { multiple = false, onChange = null } = options;
    
    // 创建上传容器
    const container = input.parentElement;
    const uploadContainer = document.createElement('div');
    uploadContainer.className = 'image-upload-container';
    
    // 创建按钮组
    const buttonGroup = document.createElement('div');
    buttonGroup.className = 'image-upload-buttons';
    
    // 上传按钮
    const uploadBtn = document.createElement('button');
    uploadBtn.type = 'button';
    uploadBtn.className = 'btn btn-secondary btn-sm';
    uploadBtn.textContent = '选择文件';
    uploadBtn.onclick = () => input.click();
    
    // 粘贴按钮
    const pasteBtn = document.createElement('button');
    pasteBtn.type = 'button';
    pasteBtn.className = 'btn btn-secondary btn-sm';
    pasteBtn.textContent = '粘贴图片';
    pasteBtn.onclick = () => handlePasteImage(input, preview, multiple, onChange);
    
    buttonGroup.appendChild(uploadBtn);
    buttonGroup.appendChild(pasteBtn);
    
    // 将按钮组插入到input之前
    input.style.display = 'none';
    container.insertBefore(buttonGroup, input);
    
    // 文件选择事件
    input.addEventListener('change', (e) => {
        handleFileSelect(e.target, preview, multiple, onChange);
    });
    
    // 粘贴事件（全局监听，但只在相关区域激活）
    let pasteHandler = null;
    const activatePaste = () => {
        if (!pasteHandler) {
            pasteHandler = (e) => {
                // 检查是否在相关的输入框附近
                if (e.target === input || input.contains(e.target) || 
                    preview.contains(e.target) || buttonGroup.contains(e.target) ||
                    container.contains(e.target)) {
                    handlePasteImage(input, preview, multiple, onChange, e);
                }
            };
            document.addEventListener('paste', pasteHandler);
        }
    };
    
    // 当输入框获得焦点时激活粘贴
    input.addEventListener('focus', activatePaste);
    buttonGroup.addEventListener('click', activatePaste);
    preview.addEventListener('click', activatePaste);
}

/**
 * 处理文件选择
 */
function handleFileSelect(input, preview, multiple, onChange) {
    const files = Array.from(input.files);
    if (files.length === 0) return;
    
    displayPreview(files, preview, multiple, input);
    
    if (onChange) {
        onChange(files, input);
    }
}

/**
 * 处理剪贴板粘贴
 */
async function handlePasteImage(input, preview, multiple, onChange, pasteEvent = null) {
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
        
        // 更新文件输入框
        const dataTransfer = new DataTransfer();
        if (multiple) {
            // 保留现有文件
            Array.from(input.files).forEach(file => dataTransfer.items.add(file));
            files.forEach(file => dataTransfer.items.add(file));
        } else {
            // 只保留第一个文件
            dataTransfer.items.add(files[0]);
        }
        input.files = dataTransfer.files;
        
        // 显示预览
        displayPreview(files, preview, multiple, input);
        
        if (onChange) {
            onChange(files, input);
        }
        
    } catch (error) {
        console.error('粘贴图片失败:', error);
        if (typeof showAlertDialog === 'function') {
            await showAlertDialog('粘贴图片失败: ' + error.message, '错误');
        } else {
            alert('粘贴图片失败: ' + error.message);
        }
    }
}

/**
 * 显示图片预览
 */
function displayPreview(files, preview, multiple, input) {
    if (!preview) return;
    
    preview.innerHTML = '';
    
    if (files.length === 0) {
        return;
    }
    
    if (multiple) {
        // 多图预览 - 网格布局
        preview.className = 'image-preview-grid';
        files.forEach((file, index) => {
            const img = createPreviewImage(file, index, input, preview);
            preview.appendChild(img);
        });
    } else {
        // 单图预览
        preview.className = 'image-preview';
        const img = createPreviewImage(files[0], 0, input, preview);
        preview.appendChild(img);
    }
}

/**
 * 创建预览图片元素
 */
function createPreviewImage(file, index, input, preview) {
    const container = document.createElement('div');
    container.className = 'preview-item';
    
    const img = document.createElement('img');
    img.alt = `预览图 ${index + 1}`;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
    
    // 删除按钮
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'preview-remove';
    removeBtn.innerHTML = '&times;';
    removeBtn.onclick = () => {
        container.remove();
        // 更新文件输入框
        const dataTransfer = new DataTransfer();
        Array.from(input.files).forEach(f => {
            if (f !== file) {
                dataTransfer.items.add(f);
            }
        });
        input.files = dataTransfer.files;
        
        // 更新预览
        const remainingFiles = Array.from(input.files);
        displayPreview(remainingFiles, preview, input.multiple, input);
    };
    
    container.appendChild(img);
    container.appendChild(removeBtn);
    
    return container;
}
