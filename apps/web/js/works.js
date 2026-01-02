/**
 * 作品管理页面脚本
 */

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('create-work-btn').addEventListener('click', openCreateWorkModal);
    document.getElementById('create-work-form').addEventListener('submit', handleCreateWork);
    
    loadWorks();
});

async function loadWorks() {
    try {
        const response = await API.listWorks();
        const works = response.works || [];
        renderWorks(works);
    } catch (error) {
        console.error('加载作品失败:', error);
        await showAlertDialog('加载作品失败: ' + error.message, '错误');
    }
}

function renderWorks(works) {
    const listEl = document.getElementById('works-list');
    
    if (works.length === 0) {
        listEl.innerHTML = '<p style="text-align: center; color: #7f8c8d; grid-column: 1/-1;">暂无作品，点击"创建新作品"开始创建</p>';
        return;
    }

    listEl.innerHTML = works.map(work => {
        const coverUrl = work.cover_images && work.cover_images.length > 0
            ? `http://localhost:8000/data/works/${work.id}/${work.cover_images[0]}`
            : '';
        
        return `
            <div class="work-card">
                ${coverUrl ? `<img src="${coverUrl}" alt="${work.name}" class="work-card-image" onerror="this.style.display='none'">` : ''}
                <div class="work-card-content">
                    <h3 class="work-card-title">${work.name}</h3>
                    <p class="work-card-description">${work.description || ''}</p>
                    <div class="work-card-actions">
                        <button class="btn btn-primary" onclick="editWorkDetails('${work.id}')">编辑详情</button>
                        <button class="btn btn-success" onclick="editEpisodes('${work.id}')">编辑剧集</button>
                        <button class="btn btn-danger" onclick="deleteWork('${work.id}')">删除</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function openCreateWorkModal() {
    const modal = document.getElementById('create-work-modal');
    modal.showModal();
}

function closeCreateWorkModal() {
    const modal = document.getElementById('create-work-modal');
    modal.close();
    document.getElementById('create-work-form').reset();
}

async function handleCreateWork(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('name', document.getElementById('work-name').value);
    formData.append('description', document.getElementById('work-description').value);
    
    try {
        const work = await API.createWork(formData);
        closeCreateWorkModal();
        loadWorks();
        await showAlertDialog('作品创建成功', '成功');
        // 自动跳转到编辑详情页面
        editWorkDetails(work.id);
    } catch (error) {
        console.error('创建作品失败:', error);
        await showAlertDialog('创建作品失败: ' + error.message, '错误');
    }
}

function editWorkDetails(workId) {
    window.location.href = `work-detail.html?work_id=${workId}`;
}

function editEpisodes(workId) {
    window.location.href = `episodes.html?work_id=${workId}`;
}

async function deleteWork(workId) {
    const confirmed = await showConfirmDialog('确定要删除这个作品吗？这将删除所有相关的剧集和内容。', '确认删除', 'danger');
    if (!confirmed) {
        return;
    }
    
    try {
        await API.deleteWork(workId);
        loadWorks();
        await showAlertDialog('删除成功', '成功');
    } catch (error) {
        console.error('删除失败:', error);
        await showAlertDialog('删除失败: ' + error.message, '错误');
    }
}

