/**
 * 素材管理页面脚本
 */

let currentType = 'characters';
let currentMaterial = null;
let imageCacheTimestamp = Date.now(); // 用于强制刷新图片

const typeNames = {
    characters: '人物角色',
    scenes: '场景',
    props: '道具',
    others: '其他'
};

document.addEventListener('DOMContentLoaded', () => {
    // 标签切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentType = btn.dataset.type;
            document.getElementById('section-title').textContent = typeNames[currentType];
            loadMaterials();
        });
    });

    // 创建按钮
    document.getElementById('create-btn').addEventListener('click', () => {
        openModal();
    });
    
    // 初始化图片上传组件
    initImageUpload('main-image', 'main-image-preview', {
        onChange: (files) => {
            if (files.length > 0) {
                // 预览已通过 displayPreview 处理
            }
        }
    });
    
    initImageUpload('aux1-image', 'aux1-image-preview', {
        onChange: (files) => {
            if (files.length > 0) {
                // 预览已通过 displayPreview 处理
            }
        }
    });
    
    initImageUpload('aux2-image', 'aux2-image-preview', {
        onChange: (files) => {
            if (files.length > 0) {
                // 预览已通过 displayPreview 处理
            }
        }
    });

    // 关闭模态框
    document.getElementById('close-modal').addEventListener('click', closeModal);
    document.getElementById('cancel-btn').addEventListener('click', closeModal);

    // 表单提交
    document.getElementById('material-form').addEventListener('submit', handleSubmit);

    // 图片预览
    ['main-image', 'aux1-image', 'aux2-image'].forEach(id => {
        document.getElementById(id).addEventListener('change', (e) => {
            previewImage(e.target, id + '-preview');
        });
    });

    // 初始加载
    loadMaterials();
});

async function loadMaterials() {
    try {
        // 更新图片缓存时间戳，强制刷新图片
        imageCacheTimestamp = Date.now();
        const response = await API.listMaterials(currentType);
        const materials = response.materials || [];
        renderMaterials(materials);
    } catch (error) {
        console.error('加载素材失败:', error);
        await showAlertDialog('加载素材失败: ' + error.message, '错误');
    }
}

function renderMaterials(materials) {
    const listEl = document.getElementById('materials-list');
    
    if (materials.length === 0) {
        listEl.innerHTML = '<p style="text-align: center; color: #7f8c8d;">暂无素材，点击"创建新素材"开始创建</p>';
        return;
    }

    listEl.innerHTML = materials.map(material => `
        <div class="material-card">
            <img src="${getImageUrl(material.main_image, currentType, material.id)}" 
                 alt="${material.name}" 
                 class="material-card-image"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3E无图片%3C/text%3E%3C/svg%3E'">
            <div class="material-card-content">
                <div class="material-card-title">${material.name}</div>
                <div class="material-card-description">${material.description || ''}</div>
                <div class="material-card-actions">
                    <button class="btn btn-primary" onclick="editMaterial('${material.id}')">编辑</button>
                    <button class="btn btn-danger" onclick="deleteMaterial('${material.id}')">删除</button>
                </div>
            </div>
        </div>
    `).join('');
}

function getImageUrl(imagePath, type, id) {
    if (!imagePath) return '';
    // 使用 API 端点，并添加时间戳避免缓存
    // 使用全局的 imageCacheTimestamp，确保同一批次加载的图片使用相同时间戳
    return `http://localhost:8000/api/materials/${type}/${id}/image/${imagePath}?t=${imageCacheTimestamp}`;
}

function openModal(material = null) {
    currentMaterial = material;
    const modal = document.getElementById('material-modal');
    const form = document.getElementById('material-form');
    
    document.getElementById('material-type').value = currentType;
    document.getElementById('modal-title').textContent = material ? '编辑素材' : '创建新素材';
    
    if (material) {
        document.getElementById('material-id').value = material.id;
        document.getElementById('material-name').value = material.name || '';
        document.getElementById('material-description').value = material.description || '';
        
        // 显示现有图片预览
        if (material.main_image) {
            document.getElementById('main-image-preview').innerHTML = 
                `<img src="${getImageUrl(material.main_image, currentType, material.id)}" alt="主图">`;
        }
        if (material.aux_images && material.aux_images[0]) {
            document.getElementById('aux1-image-preview').innerHTML = 
                `<img src="${getImageUrl(material.aux_images[0], currentType, material.id)}" alt="辅助图1">`;
        }
        if (material.aux_images && material.aux_images[1]) {
            document.getElementById('aux2-image-preview').innerHTML = 
                `<img src="${getImageUrl(material.aux_images[1], currentType, material.id)}" alt="辅助图2">`;
        }
        
        document.getElementById('main-image').required = false;
    } else {
        form.reset();
        ['main-image-preview', 'aux1-image-preview', 'aux2-image-preview'].forEach(id => {
            document.getElementById(id).innerHTML = '';
        });
        document.getElementById('main-image').required = true;
    }
    
    modal.showModal();
}

function closeModal() {
    const modal = document.getElementById('material-modal');
    modal.close();
    currentMaterial = null;
}

async function handleSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('name', document.getElementById('material-name').value);
    formData.append('description', document.getElementById('material-description').value);
    
    const mainImage = document.getElementById('main-image').files[0];
    if (mainImage) {
        formData.append('main_image', mainImage);
    }
    
    const aux1Image = document.getElementById('aux1-image').files[0];
    if (aux1Image) {
        formData.append('aux1_image', aux1Image);
    }
    
    const aux2Image = document.getElementById('aux2-image').files[0];
    if (aux2Image) {
        formData.append('aux2_image', aux2Image);
    }
    
    try {
        const materialId = document.getElementById('material-id').value;
        if (materialId) {
            await API.updateMaterial(currentType, materialId, formData);
        } else {
            await API.createMaterial(currentType, formData);
        }
        
        closeModal();
        loadMaterials();
        await showAlertDialog('保存成功', '成功');
    } catch (error) {
        console.error('保存失败:', error);
        await showAlertDialog('保存失败: ' + error.message, '错误');
    }
}

async function editMaterial(id) {
    try {
        const material = await API.getMaterial(currentType, id);
        openModal(material);
    } catch (error) {
        console.error('加载素材失败:', error);
        await showAlertDialog('加载素材失败: ' + error.message, '错误');
    }
}

async function deleteMaterial(id) {
    const confirmed = await showConfirmDialog('确定要删除这个素材吗？', '确认删除', 'danger');
    if (!confirmed) {
        return;
    }
    
    try {
        await API.deleteMaterial(currentType, id);
        loadMaterials();
        await showAlertDialog('删除成功', '成功');
    } catch (error) {
        console.error('删除失败:', error);
        await showAlertDialog('删除失败: ' + error.message, '错误');
    }
}

function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.innerHTML = `<img src="${e.target.result}" alt="预览">`;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

