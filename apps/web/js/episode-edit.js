/**
 * 剧集编辑页面脚本
 */

const urlParams = new URLSearchParams(window.location.search);
const workId = urlParams.get('work_id');
const episodeId = urlParams.get('episode_id');

let storyboard = null;
let currentShots = [];
let editingFields = {}; // 跟踪正在编辑的字段 {shotId_field: true}

// 预览面板状态管理
let isPreviewPanelVisible = false;
let previewTimer = null;
let currentPreviewIndex = 0;
let previewVideoElement = null;
let currentDialogues = []; // 当前分镜的台词数据
let imageStartTime = 0; // 图片显示的开始时间（用于字幕同步）
let subtitleTimer = null; // 字幕定时器

document.addEventListener('DOMContentLoaded', async () => {
    if (!workId || !episodeId) {
        await showAlertDialog('缺少必要参数', '错误');
        window.location.href = 'works.html';
        return;
    }

    // 设置返回按钮链接
    document.getElementById('back-to-episodes-btn').href = `episodes.html?work_id=${workId}`;
    
    // 加载剧集信息
    loadEpisodeInfo();
    
    loadScript();
    loadStoryboard();

    document.getElementById('script-form').addEventListener('submit', handleSaveScript);
    document.getElementById('generate-single-shot-storyboard-btn').addEventListener('click', handleGenerateSingleShotStoryboard);
    document.getElementById('generate-multi-shot-storyboard-btn').addEventListener('click', handleGenerateMultiShotStoryboard);
    document.getElementById('storyboard-text-form').addEventListener('submit', handleSaveStoryboardText);
    document.getElementById('confirm-storyboard-btn').addEventListener('click', handleConfirmStoryboard);
    document.getElementById('preview-btn').addEventListener('click', togglePreviewPanel);
    document.getElementById('close-preview-btn').addEventListener('click', closePreviewPanel);
    
    // 绑定生成全部分镜提示词按钮（如果存在）
    const generateAllPromptsBtn = document.getElementById('generate-all-prompts-btn');
    if (generateAllPromptsBtn) {
        generateAllPromptsBtn.addEventListener('click', generateAllShotPrompts);
    }
});

async function loadEpisodeInfo() {
    try {
        const episode = await API.getEpisode(workId, episodeId);
        document.getElementById('episode-title').textContent = episode.name || '未命名剧集';
        document.getElementById('episode-description').textContent = episode.description || '暂无描述';
    } catch (error) {
        console.error('加载剧集信息失败:', error);
        document.getElementById('episode-title').textContent = '加载失败';
        document.getElementById('episode-description').textContent = '无法加载剧集信息';
    }
}

async function loadScript() {
    try {
        const script = await API.getScript(workId, episodeId);
        document.getElementById('script-text').value = script.script || '';
        document.getElementById('expected-duration').value = script.expected_duration || 60;
        document.getElementById('shot-duration').value = script.shot_duration || 5;
    } catch (error) {
        console.error('加载脚本失败:', error);
    }
}

async function loadStoryboard() {
    try {
        const data = await API.getStoryboard(workId, episodeId);
        storyboard = data;
        
        // 检查是否已确认
        if (data.confirmed && data.shots && data.shots.length > 0) {
            // 已确认，显示分镜卡片，禁用剧本编辑
            currentShots = data.shots;
            renderShots();
            document.getElementById('shots-section').style.display = 'block';
            document.getElementById('storyboard-text-section').style.display = 'none';
            
            // 显示剧本关联素材列表（如果存在）
            if (data.related_materials && data.related_materials.length > 0) {
                renderRelatedMaterials(data.related_materials);
                document.getElementById('related-materials-section').style.display = 'block';
            } else {
                document.getElementById('related-materials-section').style.display = 'none';
            }
            
            disableScriptEditing();
        } else if (data.text) {
            // 有文本但未确认，显示分镜脚本编辑区域
            document.getElementById('storyboard-text').value = data.text;
            document.getElementById('storyboard-text-section').style.display = 'block';
            document.getElementById('shots-section').style.display = 'none';
            
            // 显示剧本关联素材列表（如果存在）
            if (data.related_materials && data.related_materials.length > 0) {
                renderStoryboardRelatedMaterials(data.related_materials);
            } else {
                document.getElementById('storyboard-related-materials-section').style.display = 'none';
            }
            
            enableScriptEditing();
        } else {
            enableScriptEditing();
        }
    } catch (error) {
        console.error('加载分镜脚本失败:', error);
        enableScriptEditing();
    }
}

function disableScriptEditing() {
    // 禁用剧本输入框
    const scriptText = document.getElementById('script-text');
    scriptText.disabled = true;
    scriptText.style.backgroundColor = '#f5f5f5';
    scriptText.style.cursor = 'not-allowed';
    
    // 隐藏原有的按钮
    const saveBtn = document.querySelector('#script-form button[type="submit"]');
    const generateBtn = document.getElementById('generate-storyboard-btn');
    if (saveBtn) saveBtn.style.display = 'none';
    if (generateBtn) generateBtn.style.display = 'none';
    
    // 显示"重新编辑剧本"按钮
    let reeditBtn = document.getElementById('reedit-script-btn');
    if (!reeditBtn) {
        reeditBtn = document.createElement('button');
        reeditBtn.id = 'reedit-script-btn';
        reeditBtn.type = 'button';
        reeditBtn.className = 'btn btn-warning';
        reeditBtn.textContent = '重新编辑剧本';
        reeditBtn.addEventListener('click', handleReeditScript);
        
        const formActions = document.querySelector('#script-form .form-actions');
        if (formActions) {
            formActions.appendChild(reeditBtn);
        }
    }
    reeditBtn.style.display = 'block';
}

function enableScriptEditing() {
    // 启用剧本输入框
    const scriptText = document.getElementById('script-text');
    scriptText.disabled = false;
    scriptText.style.backgroundColor = '';
    scriptText.style.cursor = '';
    
    // 显示原有的按钮
    const saveBtn = document.querySelector('#script-form button[type="submit"]');
    const generateBtn = document.getElementById('generate-storyboard-btn');
    if (saveBtn) saveBtn.style.display = 'block';
    if (generateBtn) generateBtn.style.display = 'block';
    
    // 隐藏"重新编辑剧本"按钮
    const reeditBtn = document.getElementById('reedit-script-btn');
    if (reeditBtn) {
        reeditBtn.style.display = 'none';
    }
}

async function handleReeditScript() {
    const confirmed = await showConfirmDialog(
        '重新编辑剧本后，如果重新生成分镜脚本，会覆盖现有的分镜。确定要继续吗？',
        '确认重新编辑'
    );
    
    if (!confirmed) {
        return;
    }
    
    // 恢复编辑状态
    enableScriptEditing();
}

async function handleSaveScript(e) {
    e.preventDefault();
    
    const script = document.getElementById('script-text').value;
    const duration = parseInt(document.getElementById('expected-duration').value);
    const shotDuration = parseInt(document.getElementById('shot-duration').value);
    
    try {
        await API.saveScript(workId, episodeId, script, duration, shotDuration);
        await showAlertDialog('剧本保存成功', '成功');
    } catch (error) {
        console.error('保存剧本失败:', error);
        await showAlertDialog('保存剧本失败: ' + error.message, '错误');
    }
}

// 生成多镜头分镜脚本（预留功能）
async function handleGenerateMultiShotStoryboard() {
    await showAlertDialog('生成多镜头分镜脚本功能开发中', '提示');
}

// 生成单镜头分镜脚本
async function handleGenerateSingleShotStoryboard() {
    const script = document.getElementById('script-text').value;
    const expectedDuration = parseInt(document.getElementById('expected-duration').value) || 60;
    const shotDuration = parseInt(document.getElementById('shot-duration').value) || 5;
    
    if (!script.trim()) {
        await showAlertDialog('请先输入剧本内容', '提示');
        return;
    }

    const confirmed = await showConfirmDialog('生成分镜脚本将覆盖现有的分镜，确定继续吗？', '确认');
    if (!confirmed) {
        return;
    }

    try {
        const btn = document.getElementById('generate-single-shot-storyboard-btn');
        btn.disabled = true;
        btn.textContent = '生成中...';

        // 获取作品关联的素材
        const work = await API.getWork(workId);
        
        // 获取素材名称列表
        const characterMaterials = [];
        const sceneMaterials = [];
        const propMaterials = [];
        
        // 获取人物素材名称
        for (const id of (work.character_materials || [])) {
            try {
                const material = await API.getMaterial('characters', id);
                if (material && material.name) {
                    characterMaterials.push(material.name);
                }
            } catch (error) {
                console.error(`获取人物素材 ${id} 失败:`, error);
            }
        }
        
        // 获取场景素材名称
        for (const id of (work.scene_materials || [])) {
            try {
                const material = await API.getMaterial('scenes', id);
                if (material && material.name) {
                    sceneMaterials.push(material.name);
                }
            } catch (error) {
                console.error(`获取场景素材 ${id} 失败:`, error);
            }
        }
        
        // 获取道具素材名称
        for (const id of (work.prop_materials || [])) {
            try {
                const material = await API.getMaterial('props', id);
                if (material && material.name) {
                    propMaterials.push(material.name);
                }
            } catch (error) {
                console.error(`获取道具素材 ${id} 失败:`, error);
            }
        }
        
        // 调用生成单镜头分镜脚本工具
        const formData = new FormData();
        formData.append('script', script);
        formData.append('expected_duration', expectedDuration.toString());
        formData.append('shot_duration', shotDuration.toString());
        formData.append('character_materials', JSON.stringify(characterMaterials));
        formData.append('scene_materials', JSON.stringify(sceneMaterials));
        formData.append('prop_materials', JSON.stringify(propMaterials));
        
        const result = await API.createToolTask('generate_single_shot_storyboard', formData);
        const taskId = result.task_id;
        
        // 轮询任务状态
        let pollCount = 0;
        const maxPolls = 150;
        const pollInterval = setInterval(async () => {
            pollCount++;
            if (pollCount > maxPolls) {
                clearInterval(pollInterval);
                btn.disabled = false;
                btn.textContent = '生成单镜头分镜脚本';
                await showAlertDialog('生成超时，请稍后查看历史记录', '提示');
                return;
            }
            
            try {
                const status = await API.getTaskStatus(taskId);
                if (status.status === 'success') {
                    clearInterval(pollInterval);
                    const taskResult = await API.getTaskResult(taskId);
                    const storyboardText = taskResult.output.text || '';
                    
                    if (!storyboardText.trim()) {
                        await showAlertDialog('生成的分镜脚本为空，请检查剧本内容', '警告');
                        btn.disabled = false;
                        btn.textContent = '生成单镜头分镜脚本';
                        return;
                    }
                    
                    // 保存分镜脚本到后端
                    await API.saveStoryboardText(workId, episodeId, storyboardText);
                    
                    // 重新加载分镜脚本
                    await loadStoryboard();
                    
                    // 显示分镜脚本编辑区域
                    document.getElementById('storyboard-text').value = storyboardText;
                    document.getElementById('storyboard-text-section').style.display = 'block';
                    document.getElementById('shots-section').style.display = 'none';
                    
                    // 尝试解析并显示剧本关联素材
                    try {
                        // 使用 tools.js 中的解析函数
                        if (window.parseStoryboard) {
                            const parsed = window.parseStoryboard(storyboardText);
                            if (parsed.related_materials && parsed.related_materials.length > 0) {
                                renderStoryboardRelatedMaterials(parsed.related_materials);
                            }
                        }
                    } catch (error) {
                        console.error('解析分镜脚本失败:', error);
                    }
                    
                    btn.disabled = false;
                    btn.textContent = '生成单镜头分镜脚本';
                    await showAlertDialog('分镜脚本生成成功，请编辑并确认', '成功');
                } else if (status.status === 'failed') {
                    clearInterval(pollInterval);
                    btn.disabled = false;
                    btn.textContent = '生成单镜头分镜脚本';
                    await showAlertDialog('生成分镜脚本失败: ' + (status.error || '未知错误'), '错误');
                }
            } catch (error) {
                console.error('轮询任务状态失败:', error);
            }
        }, 2000);
        
    } catch (error) {
        console.error('生成分镜脚本失败:', error);
        await showAlertDialog('生成分镜脚本失败: ' + error.message, '错误');
        const btn = document.getElementById('generate-single-shot-storyboard-btn');
        btn.disabled = false;
        btn.textContent = '生成单镜头分镜脚本';
    }
}

async function handleSaveStoryboardText(e) {
    e.preventDefault();
    
    const text = document.getElementById('storyboard-text').value;
    if (!text.trim()) {
        await showAlertDialog('分镜脚本内容不能为空', '提示');
        return;
    }
    
    try {
        await API.saveStoryboardText(workId, episodeId, text);
        await showAlertDialog('分镜脚本保存成功', '成功');
    } catch (error) {
        console.error('保存分镜脚本失败:', error);
        await showAlertDialog('保存分镜脚本失败: ' + error.message, '错误');
    }
}

async function handleConfirmStoryboard() {
    const text = document.getElementById('storyboard-text').value;
    if (!text.trim()) {
        await showAlertDialog('请先输入分镜脚本内容', '提示');
        return;
    }

    const confirmed = await showConfirmDialog('生成分镜后将创建分镜卡片，确定继续吗？', '确认');
    if (!confirmed) {
        return;
    }

    try {
        const btn = document.getElementById('confirm-storyboard-btn');
        btn.disabled = true;
        btn.textContent = '生成中...';

        // 先保存文本
        await API.saveStoryboardText(workId, episodeId, text);
        
        // 生成分镜卡片（会调用LLM生成提示词）
        try {
            const data = await API.confirmStoryboard(workId, episodeId);
            storyboard = data;
            currentShots = data.shots;
            
            // 隐藏分镜脚本编辑区域，显示分镜卡片
            document.getElementById('storyboard-text-section').style.display = 'none';
            renderShots();
            document.getElementById('shots-section').style.display = 'block';
            
            // 显示剧本关联素材列表（如果存在）
            if (data.related_materials && data.related_materials.length > 0) {
                renderRelatedMaterials(data.related_materials);
                document.getElementById('related-materials-section').style.display = 'block';
            } else {
                document.getElementById('related-materials-section').style.display = 'none';
            }
            
            // 禁用剧本编辑
            disableScriptEditing();
            
            await showAlertDialog('分镜卡片生成成功', '成功');
        } catch (error) {
            // 如果解析失败，显示错误提示
            if (error.message && error.message.includes('解析失败') || error.message.includes('Storyboard text not found')) {
                await showAlertDialog('分镜脚本解析失败，请检查格式是否正确。\n\n格式要求：\n第一行：剧本关联素材：素材1，素材2\n分镜1: 描述\n关联素材: 素材1\n时长: 5', '解析失败');
            } else {
                throw error;
            }
        }
    } catch (error) {
        console.error('生成分镜失败:', error);
        await showAlertDialog('生成分镜失败: ' + error.message, '错误');
    } finally {
        const btn = document.getElementById('confirm-storyboard-btn');
        btn.disabled = false;
        btn.textContent = '生成分镜';
    }
}

function renderShots() {
    const container = document.getElementById('shots-container');
    
    if (currentShots.length === 0) {
        container.innerHTML = '<p class="loading">暂无分镜</p>';
        return;
    }

    container.innerHTML = currentShots.map((shot, index) => {
        const imagePrompt = shot.image_prompt || '';
        const videoPrompt = shot.video_prompt || '';
        const referenceVideoPrompt = shot.reference_video_prompt || '';
        const audioPrompt = shot.audio_prompt || '';
        const dialoguePrompt = shot.dialogue_prompt || '';
        const description = shot.description || '';
        const duration = shot.duration || 0;
        const relatedMaterials = shot.related_materials || [];
        
        // 根据内容决定默认显示的tab
        // 优先级：参考视频 > 视频 > 图片
        let defaultTab = 'image';
        if (shot.current_video || shot.video_task_id) {
            defaultTab = 'reference';
        } else if (shot.video) {
            defaultTab = 'video';
        }
        
        return `
            <div class="shot-card" data-shot-id="${shot.id}">
                <div class="shot-card-header">
                    <span class="shot-number">分镜 ${index + 1}</span>
                </div>
                
                <!-- 分镜描述（单独显示） -->
                <div class="field-section">
                    <div class="field-label">分镜描述：</div>
                    <div class="field-content" id="${shot.id}_description_view">
                        <div class="field-view">${escapeHtml(description)}</div>
                        <button class="btn btn-sm btn-secondary" onclick="editField('${shot.id}', 'description')">编辑</button>
                    </div>
                    <div class="field-edit" id="${shot.id}_description_edit" style="display: none;">
                        <textarea class="field-textarea" id="${shot.id}_description_textarea">${escapeHtml(description)}</textarea>
                        <div class="field-edit-actions">
                            <button class="btn btn-sm btn-primary" onclick="saveField('${shot.id}', 'description')">保存</button>
                            <button class="btn btn-sm btn-secondary" onclick="cancelEditField('${shot.id}', 'description')">取消</button>
                        </div>
                    </div>
                </div>
                
                <!-- 预期时长 -->
                <div class="field-section">
                    <div class="field-label">预期时长（秒）：</div>
                    <select class="form-control" id="${shot.id}_duration_select" onchange="updateShotDuration('${shot.id}', this.value)" style="display: inline-block; width: auto; margin-left: 0.5rem;">
                        <option value="1" ${duration === 1 ? 'selected' : ''}>1</option>
                        <option value="2" ${duration === 2 ? 'selected' : ''}>2</option>
                        <option value="3" ${duration === 3 ? 'selected' : ''}>3</option>
                        <option value="4" ${duration === 4 ? 'selected' : ''}>4</option>
                        <option value="5" ${duration === 5 ? 'selected' : ''}>5</option>
                        <option value="6" ${duration === 6 ? 'selected' : ''}>6</option>
                    </select>
                </div>
                
                <!-- 生成提示词按钮 -->
                <div class="field-section" style="margin-top: 1rem;">
                    <button class="btn btn-primary" onclick="generateShotPrompts('${shot.id}')">生成提示词</button>
                </div>
                
                <!-- 提示词和内容（tab切换） -->
                <div class="prompt-tabs">
                    <button class="prompt-tab ${defaultTab === 'image' ? 'active' : ''}" onclick="switchPromptTab('${shot.id}', 'image')">图片</button>
                    <button class="prompt-tab ${defaultTab === 'video' ? 'active' : ''}" onclick="switchPromptTab('${shot.id}', 'video')">视频</button>
                    <button class="prompt-tab ${defaultTab === 'reference' ? 'active' : ''}" onclick="switchPromptTab('${shot.id}', 'reference')">参考</button>
                    <button class="prompt-tab ${defaultTab === 'audio' ? 'active' : ''}" onclick="switchPromptTab('${shot.id}', 'audio')">音频</button>
                </div>
                
                <div class="prompt-content ${defaultTab === 'image' ? 'active' : ''}" id="${shot.id}-image-prompt">
                    <div class="field-section">
                        <div class="field-label">图片提示词：</div>
                        <div class="field-content" id="${shot.id}_image_prompt_view">
                            <div class="field-view">${escapeHtml(imagePrompt)}</div>
                            <button class="btn btn-sm btn-secondary" onclick="editField('${shot.id}', 'image_prompt')">编辑</button>
                        </div>
                        <div class="field-edit" id="${shot.id}_image_prompt_edit" style="display: none;">
                            <textarea class="field-textarea" id="${shot.id}_image_prompt_textarea">${escapeHtml(imagePrompt)}</textarea>
                            <div class="field-edit-actions">
                                <button class="btn btn-sm btn-primary" onclick="saveField('${shot.id}', 'image_prompt')">保存</button>
                                <button class="btn btn-sm btn-secondary" onclick="cancelEditField('${shot.id}', 'image_prompt')">取消</button>
                            </div>
                        </div>
                    </div>
                    <div class="content-actions" style="margin-top: 1rem;">
                        <button class="btn btn-primary" onclick="generateImages('${shot.id}', '${imagePrompt.replace(/'/g, "\\'")}')">生成图片</button>
                    </div>
                    <div class="content-preview" id="${shot.id}-images" style="margin-top: 1rem;">
                        ${renderImageContent(shot)}
                    </div>
                </div>
                <div class="prompt-content ${defaultTab === 'video' ? 'active' : ''}" id="${shot.id}-video-prompt">
                    <div class="field-section">
                        <div class="field-label">视频提示词：</div>
                        <div class="field-content" id="${shot.id}_video_prompt_view">
                            <div class="field-view">${escapeHtml(videoPrompt)}</div>
                            <button class="btn btn-sm btn-secondary" onclick="editField('${shot.id}', 'video_prompt')">编辑</button>
                        </div>
                        <div class="field-edit" id="${shot.id}_video_prompt_edit" style="display: none;">
                            <textarea class="field-textarea" id="${shot.id}_video_prompt_textarea">${escapeHtml(videoPrompt)}</textarea>
                            <div class="field-edit-actions">
                                <button class="btn btn-sm btn-primary" onclick="saveField('${shot.id}', 'video_prompt')">保存</button>
                                <button class="btn btn-sm btn-secondary" onclick="cancelEditField('${shot.id}', 'video_prompt')">取消</button>
                            </div>
                        </div>
                    </div>
                    <div class="content-actions" style="margin-top: 1rem;">
                        <button class="btn btn-primary" onclick="generateVideo('${shot.id}', '${videoPrompt.replace(/'/g, "\\'")}')">生成视频</button>
                    </div>
                    <div class="content-preview" id="${shot.id}-video" style="margin-top: 1rem;">
                        ${renderVideoContent(shot)}
                    </div>
                </div>
                <div class="prompt-content ${defaultTab === 'reference' ? 'active' : ''}" id="${shot.id}-reference-prompt">
                    <div class="field-section">
                        <div class="field-label">参考视频提示词：</div>
                        <div class="field-content" id="${shot.id}_reference_video_prompt_view">
                            <div class="field-view">${escapeHtml(referenceVideoPrompt)}</div>
                            <button class="btn btn-sm btn-secondary" onclick="editField('${shot.id}', 'reference_video_prompt')">编辑</button>
                        </div>
                        <div class="field-edit" id="${shot.id}_reference_video_prompt_edit" style="display: none;">
                            <textarea class="field-textarea" id="${shot.id}_reference_video_prompt_textarea">${escapeHtml(referenceVideoPrompt)}</textarea>
                            <div class="field-edit-actions">
                                <button class="btn btn-sm btn-primary" onclick="saveField('${shot.id}', 'reference_video_prompt')">保存</button>
                                <button class="btn btn-sm btn-secondary" onclick="cancelEditField('${shot.id}', 'reference_video_prompt')">取消</button>
                            </div>
                        </div>
                    </div>
                    <div class="content-actions" style="margin-top: 1rem;">
                        <button class="btn btn-primary" onclick="generateReferenceVideo('${shot.id}')">生成视频</button>
                        <button class="btn btn-secondary" onclick="showReferenceVideoHistory('${shot.id}')" style="margin-left: 0.5rem;">历史</button>
                    </div>
                    <div class="content-preview" id="${shot.id}-reference-video" style="margin-top: 1rem;">
                        ${renderReferenceVideoContent(shot)}
                    </div>
                </div>
                <div class="prompt-content ${defaultTab === 'audio' ? 'active' : ''}" id="${shot.id}-audio-prompt">
                    <div class="field-section">
                        <div class="field-label">音频提示词：</div>
                        <div class="field-content" id="${shot.id}_audio_prompt_view">
                            <div class="field-view">${escapeHtml(audioPrompt)}</div>
                            <button class="btn btn-sm btn-secondary" onclick="editField('${shot.id}', 'audio_prompt')">编辑</button>
                        </div>
                        <div class="field-edit" id="${shot.id}_audio_prompt_edit" style="display: none;">
                            <textarea class="field-textarea" id="${shot.id}_audio_prompt_textarea">${escapeHtml(audioPrompt)}</textarea>
                            <div class="field-edit-actions">
                                <button class="btn btn-sm btn-primary" onclick="saveField('${shot.id}', 'audio_prompt')">保存</button>
                                <button class="btn btn-sm btn-secondary" onclick="cancelEditField('${shot.id}', 'audio_prompt')">取消</button>
                            </div>
                        </div>
                    </div>
                    ${dialoguePrompt ? `
                    <div class="field-section" style="margin-top: 1rem;">
                        <div class="field-label">台词提示词：</div>
                        <div class="field-content" id="${shot.id}_dialogue_prompt_view">
                            <div class="field-view">${escapeHtml(dialoguePrompt)}</div>
                            <button class="btn btn-sm btn-secondary" onclick="editField('${shot.id}', 'dialogue_prompt')">编辑</button>
                        </div>
                        <div class="field-edit" id="${shot.id}_dialogue_prompt_edit" style="display: none;">
                            <textarea class="field-textarea" id="${shot.id}_dialogue_prompt_textarea">${escapeHtml(dialoguePrompt)}</textarea>
                            <div class="field-edit-actions">
                                <button class="btn btn-sm btn-primary" onclick="saveField('${shot.id}', 'dialogue_prompt')">保存</button>
                                <button class="btn btn-sm btn-secondary" onclick="cancelEditField('${shot.id}', 'dialogue_prompt')">取消</button>
                            </div>
                        </div>
                    </div>
                    ` : ''}
                    <div class="content-actions" style="margin-top: 1rem;">
                        <button class="btn btn-primary" onclick="generateAudio('${shot.id}', '${audioPrompt.replace(/'/g, "\\'")}')">生成音频</button>
                    </div>
                    <div class="content-preview" id="${shot.id}-audio" style="margin-top: 1rem;">
                        ${renderAudioContent(shot)}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function editField(shotId, fieldName) {
    const viewDiv = document.getElementById(`${shotId}_${fieldName}_view`);
    const editDiv = document.getElementById(`${shotId}_${fieldName}_edit`);
    const textarea = document.getElementById(`${shotId}_${fieldName}_textarea`);
    
    if (viewDiv && editDiv && textarea) {
        viewDiv.style.display = 'none';
        editDiv.style.display = 'block';
        editingFields[`${shotId}_${fieldName}`] = true;
        textarea.focus();
    }
}

function cancelEditField(shotId, fieldName) {
    const viewDiv = document.getElementById(`${shotId}_${fieldName}_view`);
    const editDiv = document.getElementById(`${shotId}_${fieldName}_edit`);
    const textarea = document.getElementById(`${shotId}_${fieldName}_textarea`);
    const shot = currentShots.find(s => s.id === shotId);
    
    if (viewDiv && editDiv && textarea && shot) {
        // 恢复原始值
        const originalValue = shot[fieldName] || '';
        textarea.value = originalValue;
        
        viewDiv.style.display = 'block';
        editDiv.style.display = 'none';
        delete editingFields[`${shotId}_${fieldName}`];
    }
}

async function saveField(shotId, fieldName) {
    const textarea = document.getElementById(`${shotId}_${fieldName}_textarea`);
    const shot = currentShots.find(s => s.id === shotId);
    
    if (!textarea || !shot) return;
    
    const newValue = textarea.value;
    
    try {
        // 构建更新数据
        const updateData = {
            description: fieldName === 'description' ? newValue : null,
            image_prompt: fieldName === 'image_prompt' ? newValue : null,
            video_prompt: fieldName === 'video_prompt' ? newValue : null,
            audio_prompt: fieldName === 'audio_prompt' ? newValue : null,
            reference_video_prompt: fieldName === 'reference_video_prompt' ? newValue : null,
            dialogue_prompt: fieldName === 'dialogue_prompt' ? newValue : null
        };
        
        await API.updateShot(
            workId, 
            episodeId, 
            shotId,
            updateData.description,
            updateData.image_prompt,
            updateData.video_prompt,
            updateData.audio_prompt,
            null,
            updateData.reference_video_prompt,
            updateData.dialogue_prompt
        );
        
        // 更新本地数据
        shot[fieldName] = newValue;
        
        // 更新显示
        const viewDiv = document.getElementById(`${shotId}_${fieldName}_view`);
        const editDiv = document.getElementById(`${shotId}_${fieldName}_edit`);
        const viewContent = viewDiv.querySelector('.field-view');
        
        if (viewContent) {
            viewContent.textContent = newValue;
        }
        
        viewDiv.style.display = 'block';
        editDiv.style.display = 'none';
        delete editingFields[`${shotId}_${fieldName}`];
        
        await showAlertDialog('保存成功', '成功');
    } catch (error) {
        console.error('保存字段失败:', error);
        await showAlertDialog('保存失败: ' + error.message, '错误');
    }
}

function renderImageContent(shot) {
    if (shot.image_candidates && shot.image_candidates.length > 0) {
        const selected = shot.selected_image || '';
        return `
            <div class="image-candidates">
                ${shot.image_candidates.map(candidate => {
                    const isSelected = candidate.path === selected;
                    return `
                        <div class="image-candidate ${isSelected ? 'selected' : ''}" 
                             onclick="selectImage('${shot.id}', '${candidate.path}')">
                            <img src="http://localhost:8000/data/works/${workId}/episodes/${episodeId}/shots/${shot.id}/${candidate.path}" 
                                 alt="候选图片" 
                                 onerror="this.parentElement.style.display='none'">
                            ${isSelected ? '<span class="select-badge">已选择</span>' : ''}
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
    return '<p style="color: #7f8c8d;">暂无图片，点击"生成图片"开始生成</p>';
}

function renderVideoContent(shot) {
    if (shot.video) {
        return `
            <div class="content-preview">
                <video controls>
                    <source src="http://localhost:8000/data/works/${workId}/episodes/${episodeId}/shots/${shot.id}/${shot.video}" type="video/mp4">
                </video>
                <button class="btn btn-secondary" onclick="regenerateVideo('${shot.id}')" style="margin-top: 0.5rem;">重新生成</button>
            </div>
        `;
    }
    return '<p style="color: #7f8c8d;">暂无视频，点击"生成视频"开始生成</p>';
}

function renderAudioContent(shot) {
    if (shot.audio) {
        return `
            <div class="content-preview">
                <audio controls>
                    <source src="http://localhost:8000/data/works/${workId}/episodes/${episodeId}/shots/${shot.id}/${shot.audio}" type="audio/mpeg">
                </audio>
                <button class="btn btn-secondary" onclick="regenerateAudio('${shot.id}')" style="margin-top: 0.5rem;">重新生成</button>
            </div>
        `;
    }
    return '<p style="color: #7f8c8d;">暂无音频，点击"生成音频"开始生成</p>';
}

function switchPromptTab(shotId, type) {
    const card = document.querySelector(`[data-shot-id="${shotId}"]`);
    if (!card) return;
    
    card.querySelectorAll('.prompt-tab').forEach(tab => tab.classList.remove('active'));
    card.querySelectorAll('.prompt-content').forEach(content => content.classList.remove('active'));
    
    const tabButton = card.querySelector(`[onclick*="switchPromptTab('${shotId}', '${type}')"]`);
    const contentDiv = document.getElementById(`${shotId}-${type}-prompt`);
    
    if (tabButton) tabButton.classList.add('active');
    if (contentDiv) contentDiv.classList.add('active');
}

async function generateImages(shotId, prompt) {
    try {
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = '生成中...';

        const result = await API.generateImages(workId, episodeId, shotId, prompt);
        const shot = currentShots.find(s => s.id === shotId);
        if (shot) {
            shot.image_candidates = result.candidates;
            document.getElementById(`${shotId}-images`).innerHTML = renderImageContent(shot);
        }
    } catch (error) {
        console.error('生成图片失败:', error);
        await showAlertDialog('生成图片失败: ' + error.message, '错误');
    } finally {
        const btn = event.target;
        btn.disabled = false;
        btn.textContent = '生成图片';
    }
}

async function selectImage(shotId, imagePath) {
    try {
        await API.selectImage(workId, episodeId, shotId, imagePath);
        const shot = currentShots.find(s => s.id === shotId);
        if (shot) {
            shot.selected_image = imagePath;
            const imagesContainer = document.getElementById(`${shotId}-images`);
            if (imagesContainer) {
                imagesContainer.innerHTML = renderImageContent(shot);
            }
        }
    } catch (error) {
        console.error('选择图片失败:', error);
        await showAlertDialog('选择图片失败: ' + error.message, '错误');
    }
}

async function generateVideo(shotId, prompt) {
    try {
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = '生成中...';

        const result = await API.generateVideo(workId, episodeId, shotId, prompt);
        const shot = currentShots.find(s => s.id === shotId);
        if (shot) {
            shot.video = result.video_path;
            const videoContainer = document.getElementById(`${shotId}-video`);
            if (videoContainer) {
                videoContainer.innerHTML = renderVideoContent(shot);
            }
        }
    } catch (error) {
        console.error('生成视频失败:', error);
        await showAlertDialog('生成视频失败: ' + error.message, '错误');
    } finally {
        const btn = event.target;
        btn.disabled = false;
        btn.textContent = '生成视频';
    }
}

async function regenerateVideo(shotId) {
    const shot = currentShots.find(s => s.id === shotId);
    if (shot) {
        generateVideo(shotId, shot.video_prompt || '');
    }
}

async function generateAudio(shotId, prompt) {
    try {
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = '生成中...';

        const result = await API.generateAudio(workId, episodeId, shotId, prompt);
        const shot = currentShots.find(s => s.id === shotId);
        if (shot) {
            shot.audio = result.audio_path;
            const audioContainer = document.getElementById(`${shotId}-audio`);
            if (audioContainer) {
                audioContainer.innerHTML = renderAudioContent(shot);
            }
        }
    } catch (error) {
        console.error('生成音频失败:', error);
        await showAlertDialog('生成音频失败: ' + error.message, '错误');
    } finally {
        const btn = event.target;
        btn.disabled = false;
        btn.textContent = '生成音频';
    }
}

async function regenerateAudio(shotId) {
    const shot = currentShots.find(s => s.id === shotId);
    if (shot) {
        generateAudio(shotId, shot.audio_prompt || '');
    }
}

// 切换预览面板显示/隐藏
function togglePreviewPanel() {
    const panel = document.getElementById('preview-panel');
    if (!panel) return;
    
    if (isPreviewPanelVisible) {
        closePreviewPanel();
    } else {
        openPreviewPanel();
    }
}

// 打开预览面板
function openPreviewPanel() {
    const panel = document.getElementById('preview-panel');
    if (!panel) return;
    
    panel.style.display = 'block';
    isPreviewPanelVisible = true;
    startPreview();
}

// 关闭预览面板
function closePreviewPanel() {
    const panel = document.getElementById('preview-panel');
    if (!panel) return;
    
    panel.style.display = 'none';
    isPreviewPanelVisible = false;
    stopPreview();
}

// 解析台词提示词
function parseDialoguePrompt(dialoguePrompt) {
    if (!dialoguePrompt || typeof dialoguePrompt !== 'string' || dialoguePrompt.trim() === '') {
        return [];
    }
    
    const dialogues = [];
    // 匹配格式：3～4秒:【角色描述】:"台词内容"
    // 支持多种格式：
    // - 3～4秒:【角色描述】:"台词内容"
    // - 3-4秒:【角色描述】:"台词内容"
    // - 3到4秒:【角色描述】:"台词内容"
    // 正则表达式：(\d+)[～\-到](\d+)秒:【([^】]+)】:"([^"]+)"
    // 使用非贪婪匹配，支持多行
    const regex = /(\d+)[～\-到](\d+)秒\s*:\s*【([^】]+)】\s*:\s*"([^"]+)"/g;
    let match;
    
    while ((match = regex.exec(dialoguePrompt)) !== null) {
        const startTime = parseFloat(match[1]);
        const endTime = parseFloat(match[2]);
        const characterDesc = match[3].trim();
        const dialogueText = match[4].trim();
        
        if (startTime >= 0 && endTime > startTime && characterDesc && dialogueText) {
            dialogues.push({
                startTime: startTime,
                endTime: endTime,
                characterDesc: characterDesc,
                dialogueText: dialogueText
            });
        }
    }
    
    // 按开始时间排序
    dialogues.sort((a, b) => a.startTime - b.startTime);
    
    console.log('解析台词结果:', dialogues);
    return dialogues;
}

// 显示字幕
function showSubtitle(dialogue) {
    const subtitleEl = document.getElementById('preview-subtitle');
    const subtitleContainer = document.getElementById('preview-subtitle-container');
    
    if (!subtitleEl) {
        console.error('字幕元素不存在！');
        return;
    }
    
    if (!subtitleContainer) {
        console.error('字幕容器不存在！');
        return;
    }
    
    if (dialogue) {
        subtitleEl.innerHTML = `<span class="subtitle-character">【${escapeHtml(dialogue.characterDesc)}】</span><span class="subtitle-text">"${escapeHtml(dialogue.dialogueText)}"</span>`;
        subtitleEl.style.display = 'block';
        subtitleContainer.style.display = 'block'; // 确保容器也显示
        console.log('显示字幕:', dialogue.characterDesc, dialogue.dialogueText);
    } else {
        subtitleEl.style.display = 'none';
        subtitleEl.innerHTML = '';
        // 注意：不隐藏容器，因为可能还有其他台词要显示
    }
}

// 清除字幕
function clearSubtitle() {
    const subtitleEl = document.getElementById('preview-subtitle');
    if (subtitleEl) {
        subtitleEl.style.display = 'none';
        subtitleEl.innerHTML = '';
    }
    
    // 清除字幕定时器
    if (subtitleTimer) {
        clearTimeout(subtitleTimer);
        subtitleTimer = null;
    }
    
    currentDialogues = [];
}

// 根据时间更新字幕（用于视频）
function updateSubtitleForTime(currentTime) {
    if (currentDialogues.length === 0) {
        showSubtitle(null);
        return;
    }
    
    // 查找当前时间应该显示的台词
    let activeDialogue = null;
    for (const dialogue of currentDialogues) {
        if (currentTime >= dialogue.startTime && currentTime <= dialogue.endTime) {
            activeDialogue = dialogue;
            break;
        }
    }
    
    // 调试信息（每秒输出一次，帮助诊断问题）
    const currentSecond = Math.floor(currentTime);
    if (currentSecond !== updateSubtitleForTime.lastLoggedSecond) {
        updateSubtitleForTime.lastLoggedSecond = currentSecond;
        console.log('当前播放时间:', currentTime.toFixed(2), '秒, 台词数量:', currentDialogues.length, '找到台词:', activeDialogue ? activeDialogue.dialogueText.substring(0, 20) + '...' : '无');
    }
    
    showSubtitle(activeDialogue);
}

// 开始图片字幕显示（用于图片）
function startImageSubtitleDisplay(duration) {
    if (currentDialogues.length === 0) {
        return;
    }
    
    // 清除之前的定时器
    if (subtitleTimer) {
        clearTimeout(subtitleTimer);
        subtitleTimer = null;
    }
    
    // 按时间顺序安排字幕显示
    const now = Date.now();
    const elapsed = 0; // 从0秒开始
    
    for (const dialogue of currentDialogues) {
        if (dialogue.startTime >= duration) {
            continue; // 跳过超出图片显示时长的台词
        }
        
        const startDelay = dialogue.startTime * 1000;
        const endDelay = Math.min(dialogue.endTime * 1000, duration * 1000);
        
        // 设置显示字幕的定时器
        setTimeout(() => {
            if (isPreviewPanelVisible) {
                showSubtitle(dialogue);
            }
        }, startDelay);
        
        // 设置隐藏字幕的定时器
        setTimeout(() => {
            if (isPreviewPanelVisible) {
                showSubtitle(null);
            }
        }, endDelay);
    }
}

// 停止预览
function stopPreview() {
    // 清除定时器
    if (previewTimer) {
        clearTimeout(previewTimer);
        previewTimer = null;
    }
    
    // 停止视频播放
    if (previewVideoElement) {
        previewVideoElement.pause();
        previewVideoElement.src = '';
        previewVideoElement = null;
    }
    
    // 清除字幕
    clearSubtitle();
    
    // 重置索引
    currentPreviewIndex = 0;
}

// 开始预览
function startPreview() {
    // 重置状态
    stopPreview();
    currentPreviewIndex = 0;
    
    // 获取排序后的分镜列表（按order或索引）
    const sortedShots = [...currentShots].sort((a, b) => {
        if (a.order !== undefined && b.order !== undefined) {
            return a.order - b.order;
        }
        return 0;
    });
    
    if (sortedShots.length === 0) {
        const content = document.getElementById('preview-panel-content');
        if (content) {
            content.innerHTML = '<p style="text-align: center; color: #7f8c8d; padding: 2rem;">暂无可预览的内容</p>';
        }
        return;
    }
    
    // 开始播放第一个分镜
    playNextShot(sortedShots);
}

// 获取分镜内容（按优先级）
function getShotContent(shot) {
    // 优先级1: 参考tab的视频
    if (shot.current_video) {
        const videoUrl = shot.current_video.startsWith('http') 
            ? shot.current_video 
            : `http://localhost:8000${shot.current_video}`;
        return { type: 'video', url: videoUrl };
    }
    
    // 优先级2: 视频tab的视频
    if (shot.video) {
        const videoUrl = `http://localhost:8000/data/works/${workId}/episodes/${episodeId}/shots/${shot.id}/${shot.video}`;
        return { type: 'video', url: videoUrl };
    }
    
    // 优先级3: 已选择的图片
    if (shot.selected_image) {
        const imageUrl = `http://localhost:8000/data/works/${workId}/episodes/${episodeId}/shots/${shot.id}/${shot.selected_image}`;
        return { type: 'image', url: imageUrl, duration: shot.duration || 5 };
    }
    
    // 优先级4: 第一张候选图片
    if (shot.image_candidates && shot.image_candidates.length > 0) {
        const firstCandidate = shot.image_candidates[0];
        const imageUrl = `http://localhost:8000/data/works/${workId}/episodes/${episodeId}/shots/${shot.id}/${firstCandidate.path}`;
        return { type: 'image', url: imageUrl, duration: shot.duration || 5 };
    }
    
    return null;
}

// 播放下一个分镜
async function playNextShot(sortedShots) {
    // 如果面板已关闭，停止播放
    if (!isPreviewPanelVisible) {
        return;
    }
    
    // 清除当前字幕
    clearSubtitle();
    
    // 跳过没有内容的分镜
    while (currentPreviewIndex < sortedShots.length) {
        const shot = sortedShots[currentPreviewIndex];
        const content = getShotContent(shot);
        
        if (content) {
            await displayShotContent(content, sortedShots, shot);
            return;
        }
        
        // 没有内容，跳过
        currentPreviewIndex++;
    }
    
    // 所有分镜都播放完了
    const contentEl = document.getElementById('preview-panel-content');
    if (contentEl) {
        contentEl.innerHTML = '<p style="text-align: center; color: #7f8c8d; padding: 2rem;">预览结束</p>';
    }
    clearSubtitle();
}

// 显示分镜内容
async function displayShotContent(content, sortedShots, shot) {
    const contentEl = document.getElementById('preview-panel-content');
    if (!contentEl) return;
    
    // 解析台词提示词（必须在清除字幕之前解析，避免丢失台词数据）
    const subtitleContainer = document.getElementById('preview-subtitle-container');
    
    // 先保存当前分镜的台词数据（在清除之前）
    let shotDialogues = [];
    if (shot && shot.dialogue_prompt) {
        shotDialogues = parseDialoguePrompt(shot.dialogue_prompt);
        console.log('分镜ID:', shot.id, '解析台词提示词:', shot.dialogue_prompt);
        console.log('解析后的台词数据:', shotDialogues);
    }
    
    // 清除之前的字幕（这会清空 currentDialogues）
    clearSubtitle();
    
    // 立即恢复当前分镜的台词数据
    currentDialogues = shotDialogues;
    // 显示字幕容器（如果有有效的台词）
    if (subtitleContainer) {
        if (currentDialogues.length > 0) {
            subtitleContainer.style.display = 'block';
            console.log('显示字幕容器，台词数量:', currentDialogues.length);
        } else {
            subtitleContainer.style.display = 'none';
            console.log('没有有效台词，隐藏字幕容器');
        }
    } else {
        console.error('字幕容器不存在！');
    }
    
    if (content.type === 'video') {
        // 先停止并清理旧的 video 元素
        if (previewVideoElement) {
            // 先暂停并移除事件监听器
            previewVideoElement.pause();
            previewVideoElement.src = '';
            // 克隆节点以移除所有事件监听器
            const oldVideo = previewVideoElement;
            if (oldVideo.parentNode) {
                oldVideo.parentNode.removeChild(oldVideo);
            }
            previewVideoElement = null;
        }
        
        // 清空内容区域
        contentEl.innerHTML = '';
        
        // 创建新的 video 元素
        previewVideoElement = document.createElement('video');
        previewVideoElement.controls = true;
        previewVideoElement.style.width = '100%';
        previewVideoElement.style.maxHeight = '600px';
        previewVideoElement.style.margin = '0 auto';
        previewVideoElement.style.display = 'block';
        
        // 标记是否已经处理过错误，避免重复处理
        let errorHandled = false;
        let endedHandled = false;
        
        // 监听视频结束事件
        previewVideoElement.addEventListener('ended', () => {
            if (endedHandled || !isPreviewPanelVisible) return;
            endedHandled = true;
            clearSubtitle();
            currentPreviewIndex++;
            playNextShot(sortedShots);
        });
        
        // 监听视频加载失败
        previewVideoElement.addEventListener('error', (e) => {
            if (errorHandled || !isPreviewPanelVisible) return;
            errorHandled = true;
            console.error('视频加载失败:', content.url, previewVideoElement.error);
            // 注意：不要在这里调用 clearSubtitle()，因为可能会影响下一个视频的字幕
            // 只在切换到下一个视频时清除字幕
            // 延迟一下再切换到下一个，避免立即切换导致的问题
            setTimeout(() => {
                if (isPreviewPanelVisible && !endedHandled) {
                    clearSubtitle();
                    currentPreviewIndex++;
                    playNextShot(sortedShots);
                }
            }, 1000);
        });
        
        // 监听视频时间更新，用于字幕同步
        // 使用闭包捕获当前的 currentDialogues，确保能访问到最新的值
        const handleTimeUpdate = () => {
            // 重新获取最新的 currentDialogues（因为可能在切换视频时被更新）
            // 注意：这里直接使用外部的 currentDialogues，因为它是全局变量
            if (currentDialogues.length > 0 && previewVideoElement && !errorHandled) {
                const currentTime = previewVideoElement.currentTime;
                updateSubtitleForTime(currentTime);
            } else {
                // 如果没有台词，确保字幕隐藏
                showSubtitle(null);
            }
        };
        previewVideoElement.addEventListener('timeupdate', handleTimeUpdate);
        
        // 添加调试：监听视频加载完成
        // 使用闭包捕获当前的 currentDialogues，确保能访问到正确的值
        const dialoguesForThisVideo = currentDialogues.slice(); // 复制当前台词数组
        previewVideoElement.addEventListener('loadeddata', () => {
            // 使用闭包中的 dialoguesForThisVideo，而不是全局的 currentDialogues
            // 因为 currentDialogues 可能在视频加载过程中被其他地方修改
            console.log('视频加载完成，闭包中的台词数量:', dialoguesForThisVideo.length);
            console.log('全局 currentDialogues 数量:', currentDialogues.length);
            
            // 如果闭包中有台词，但全局 currentDialogues 被清空了，恢复它
            if (dialoguesForThisVideo.length > 0 && currentDialogues.length === 0) {
                console.warn('检测到 currentDialogues 被清空，正在恢复...');
                currentDialogues = dialoguesForThisVideo.slice(); // 恢复台词数据
            }
            
            if (currentDialogues.length > 0) {
                console.log('台词数据:', currentDialogues);
                // 立即更新一次字幕，确保字幕显示
                if (previewVideoElement && !errorHandled) {
                    updateSubtitleForTime(previewVideoElement.currentTime || 0);
                }
            } else {
                console.log('当前视频没有台词数据');
            }
        });
        
        contentEl.appendChild(previewVideoElement);
        
        // 设置视频源
        previewVideoElement.src = content.url;
        
        // 等待视频加载并播放
        try {
            // 等待视频可以播放
            await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    previewVideoElement.removeEventListener('canplay', handleCanPlay);
                    previewVideoElement.removeEventListener('error', handleError);
                    reject(new Error('视频加载超时'));
                }, 10000); // 10秒超时
                
                const handleCanPlay = () => {
                    clearTimeout(timeout);
                    previewVideoElement.removeEventListener('canplay', handleCanPlay);
                    previewVideoElement.removeEventListener('error', handleError);
                    resolve();
                };
                const handleError = (e) => {
                    clearTimeout(timeout);
                    previewVideoElement.removeEventListener('canplay', handleCanPlay);
                    previewVideoElement.removeEventListener('error', handleError);
                    reject(e);
                };
                previewVideoElement.addEventListener('canplay', handleCanPlay, { once: true });
                previewVideoElement.addEventListener('error', handleError, { once: true });
                previewVideoElement.load();
            });
            
            // 播放视频
            try {
                await previewVideoElement.play();
                // 初始化字幕显示（延迟一点确保视频已开始播放和 currentDialogues 已设置）
                setTimeout(() => {
                    if (currentDialogues.length > 0 && previewVideoElement && isPreviewPanelVisible && !errorHandled) {
                        updateSubtitleForTime(previewVideoElement.currentTime || 0);
                    }
                }, 300);
            } catch (playError) {
                // AbortError 是正常的（如果用户暂停或切换视频），不需要处理
                if (playError.name !== 'AbortError' && playError.name !== 'NotAllowedError') {
                    console.error('视频播放失败:', playError);
                    // 对于非 AbortError，延迟切换到下一个
                    if (isPreviewPanelVisible && !errorHandled && !endedHandled) {
                        setTimeout(() => {
                            currentPreviewIndex++;
                            playNextShot(sortedShots);
                        }, 1000);
                    }
                }
            }
        } catch (loadError) {
            // 加载错误已经由 error 事件处理器处理，这里只记录日志
            if (!errorHandled) {
                console.error('视频加载过程出错:', loadError);
            }
        }
        
    } else if (content.type === 'image') {
        // 清除之前的video元素
        if (previewVideoElement) {
            previewVideoElement = null;
        }
        
        // 显示图片
        const img = document.createElement('img');
        img.src = content.url;
        img.style.maxWidth = '100%';
        img.style.maxHeight = '600px';
        img.style.objectFit = 'contain';
        img.style.margin = '0 auto';
        img.style.display = 'block';
        
        // 图片加载失败处理
        img.onerror = () => {
            console.error('图片加载失败:', content.url);
            contentEl.innerHTML = '<p style="text-align: center; color: #7f8c8d; padding: 2rem;">图片加载失败</p>';
            clearSubtitle();
            // 1秒后切换到下一个
            previewTimer = setTimeout(() => {
                currentPreviewIndex++;
                playNextShot(sortedShots);
            }, 1000);
        };
        
        contentEl.innerHTML = '';
        contentEl.appendChild(img);
        
        // 初始化图片显示时间
        imageStartTime = Date.now();
        
        // 如果有台词，开始字幕显示逻辑
        if (currentDialogues.length > 0) {
            startImageSubtitleDisplay(content.duration || 5);
        }
        
        // 设置定时器，在指定时长后切换到下一个分镜
        const duration = (content.duration || 5) * 1000;
        previewTimer = setTimeout(() => {
            clearSubtitle();
            currentPreviewIndex++;
            playNextShot(sortedShots);
        }, duration);
    }
}

async function showPreview() {
    const modal = document.getElementById('preview-modal');
    const container = document.getElementById('preview-container');
    
    container.innerHTML = '<p class="loading">加载预览</p>';
    modal.showModal();

    // 加载所有分镜的内容
    let previewHTML = '';
    for (let shot of currentShots) {
        const shotData = await API.getShot(workId, episodeId, shot.id);
        
        if (shotData.video) {
            previewHTML += `
                <div class="preview-shot">
                    <video controls style="width: 100%; max-height: 500px;">
                        <source src="http://localhost:8000/data/works/${workId}/episodes/${episodeId}/shots/${shot.id}/${shotData.video}" type="video/mp4">
                    </video>
                </div>
            `;
        } else if (shotData.selected_image) {
            previewHTML += `
                <div class="preview-shot">
                    <img src="http://localhost:8000/data/works/${workId}/episodes/${episodeId}/shots/${shot.id}/${shotData.selected_image}" 
                         style="width: 100%; max-height: 500px; object-fit: contain;">
                </div>
            `;
        }
        
        if (shotData.audio) {
            previewHTML += `
                <audio controls style="width: 100%; margin-top: 1rem;">
                    <source src="http://localhost:8000/data/works/${workId}/episodes/${episodeId}/shots/${shot.id}/${shotData.audio}" type="audio/mpeg">
                </audio>
            `;
        }
    }

    container.innerHTML = previewHTML || '<p style="text-align: center; color: #7f8c8d;">暂无可预览的内容</p>';
}

// 渲染剧本关联素材列表（在分镜脚本编辑区域中显示）
function renderStoryboardRelatedMaterials(materials) {
    const section = document.getElementById('storyboard-related-materials-section');
    const list = document.getElementById('storyboard-related-materials-list');
    
    if (!section || !list) return;
    
    if (!materials || materials.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    list.innerHTML = materials.map(material => {
        return `<span class="material-tag" style="display: inline-block; margin: 0.25rem; padding: 0.25rem 0.5rem; background: #3498db; color: white; border-radius: 4px; cursor: pointer;" onclick="viewMaterialDetailByName('${escapeHtml(material)}')">${escapeHtml(material)}</span>`;
    }).join('');
}

// 渲染剧本关联素材列表（在剧本和分镜卡片之间显示）
async function renderRelatedMaterials(materials) {
    const section = document.getElementById('related-materials-section');
    const list = document.getElementById('related-materials-list');
    
    if (!section || !list) return;
    
    if (!materials || materials.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    // 显示加载状态
    list.innerHTML = '<div style="text-align: center; padding: 1rem; color: #7f8c8d;">加载中...</div>';
    section.style.display = 'block';
    
    try {
        // 获取作品关联的所有素材
        const work = await API.getWork(workId);
        const allMaterialIds = [
            ...(work.character_materials || []).map(id => ({id, type: 'characters'})),
            ...(work.scene_materials || []).map(id => ({id, type: 'scenes'})),
            ...(work.prop_materials || []).map(id => ({id, type: 'props'}))
        ];
        
        // 根据名称匹配素材
        const materialItems = [];
        for (const materialName of materials) {
            let found = false;
            for (const {id, type} of allMaterialIds) {
                try {
                    const material = await API.getMaterial(type, id);
                    if (material && material.name === materialName) {
                        materialItems.push({
                            ...material,
                            id,
                            material_type: type
                        });
                        found = true;
                        break;
                    }
                } catch (error) {
                    console.error(`获取素材 ${id} 失败:`, error);
                }
            }
            
            // 如果没找到，仍然显示名称（不显示图片）
            if (!found) {
                materialItems.push({
                    name: materialName,
                    id: null,
                    material_type: null,
                    main_image: null
                });
            }
        }
        
        // 渲染素材列表
        if (materialItems.length === 0) {
            list.innerHTML = '<div style="text-align: center; padding: 1rem; color: #7f8c8d;">暂无素材</div>';
            return;
        }
        
        list.innerHTML = materialItems.map(material => {
            const imageUrl = material.main_image && material.id && material.material_type ? 
                `http://localhost:8000/api/materials/${material.material_type}/${material.id}/image/${material.main_image}` : 
                'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22120%22 height=%22120%22%3E%3Crect fill=%22%23ddd%22 width=%22120%22 height=%22120%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3E无图片%3C/text%3E%3C/svg%3E';
            
            const onClick = material.id && material.material_type ? 
                `onclick="viewMaterialDetailById('${material.material_type}', '${material.id}')"` : 
                `onclick="viewMaterialDetailByName('${escapeHtml(material.name)}')"`;
            
            return `
                <div class="related-material-item" ${onClick} style="cursor: pointer;">
                    <img src="${imageUrl}" 
                         alt="${escapeHtml(material.name || '')}"
                         onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22120%22 height=%22120%22%3E%3Crect fill=%22%23ddd%22 width=%22120%22 height=%22120%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3E无图片%3C/text%3E%3C/svg%3E'">
                    <div class="related-material-item-name">${escapeHtml(material.name || '未命名')}</div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('加载素材列表失败:', error);
        list.innerHTML = '<div style="text-align: center; padding: 1rem; color: #dc3545;">加载失败</div>';
    }
}

// 根据ID查看素材详情
async function viewMaterialDetailById(type, id) {
    try {
        // 直接获取素材信息
        const material = await API.getMaterial(type, id);
        
        // 构建图片URL
        const imageUrl = material.main_image ? 
            `http://localhost:8000/api/materials/${type}/${id}/image/${material.main_image}` : '';
        
        // 创建并显示详情对话框
        const dialogId = 'episode-material-detail-dialog';
        let dialog = document.getElementById(dialogId);
        
        if (!dialog) {
            // 创建对话框
            dialog = document.createElement('dialog');
            dialog.id = dialogId;
            dialog.className = 'modal';
            dialog.innerHTML = `
                <div class="modal-content" style="max-width: 600px;">
                    <div class="modal-header">
                        <h3>素材详情</h3>
                        <button class="modal-close" onclick="document.getElementById('${dialogId}').close()">&times;</button>
                    </div>
                    <div id="${dialogId}-content" class="modal-body">
                        <!-- 内容将动态填充 -->
                    </div>
                </div>
            `;
            document.body.appendChild(dialog);
        }
        
        const content = document.getElementById(`${dialogId}-content`);
        content.innerHTML = `
            <div style="text-align: center; margin-bottom: 1rem;">
                ${imageUrl ? 
                    `<img src="${imageUrl}" alt="${escapeHtml(material.name || '')}" style="max-width: 100%; max-height: 400px; object-fit: contain;" onerror="this.parentElement.innerHTML='<div style=\\'width: 100%; height: 400px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #999;\\'>图片加载失败</div>'">` : 
                    '<div style="width: 100%; height: 400px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #999;">无图片</div>'}
            </div>
            <div>
                <h4>${escapeHtml(material.name || '未命名')}</h4>
                <p><strong>类型：</strong>${type === 'characters' ? '人物' : type === 'scenes' ? '场景' : type === 'props' ? '道具' : '其他'}</p>
                <p><strong>描述：</strong>${escapeHtml(material.description || '无描述')}</p>
            </div>
        `;
        
        dialog.showModal();
    } catch (error) {
        console.error('查看素材详情失败:', error);
        await showAlertDialog('素材不存在: ' + (error.message || '无法获取素材信息'), '错误');
    }
}

// 查看素材详情（根据名称）
async function viewMaterialDetailByName(materialName) {
    // 获取作品关联的素材，查找匹配的素材
    try {
        const work = await API.getWork(workId);
        const allMaterialIds = [
            ...(work.character_materials || []).map(id => ({id, type: 'characters'})),
            ...(work.scene_materials || []).map(id => ({id, type: 'scenes'})),
            ...(work.prop_materials || []).map(id => ({id, type: 'props'}))
        ];
        
        // 查找匹配的素材
        for (const {id, type} of allMaterialIds) {
            try {
                const material = await API.getMaterial(type, id);
                if (material && material.name === materialName) {
                    // 打开素材详情对话框（使用 tools.js 中的函数）
                    if (window.viewMaterialDetail) {
                        window.viewMaterialDetail(id, type);
                    } else {
                        await showAlertDialog(`素材名称: ${materialName}\n素材类型: ${type === 'characters' ? '人物' : type === 'scenes' ? '场景' : '道具'}`, '素材详情');
                    }
                    return;
                }
            } catch (error) {
                console.error(`获取素材 ${id} 失败:`, error);
            }
        }
        
        await showAlertDialog(`未找到素材: ${materialName}`, '提示');
    } catch (error) {
        console.error('查看素材详情失败:', error);
        await showAlertDialog('查看素材详情失败: ' + error.message, '错误');
    }
}

// 更新分镜时长
async function updateShotDuration(shotId, duration) {
    const shot = currentShots.find(s => s.id === shotId);
    if (!shot) return;
    
    try {
        shot.duration = parseInt(duration);
        // 保存到后端
        await API.updateShot(workId, episodeId, shotId, null, null, null, null, duration);
    } catch (error) {
        console.error('更新分镜时长失败:', error);
        await showAlertDialog('更新分镜时长失败: ' + error.message, '错误');
    }
}

// 生成分镜提示词
async function generateShotPrompts(shotId) {
    const shot = currentShots.find(s => s.id === shotId);
    if (!shot) return;
    
    const description = shot.description || '';
    const duration = shot.duration || 5;
    const relatedMaterials = shot.related_materials || [];
    
    if (!description.trim()) {
        await showAlertDialog('请先填写分镜描述', '提示');
        return;
    }
    
    // 获取按钮并更新状态
    const card = document.querySelector(`[data-shot-id="${shotId}"]`);
    const btn = card ? card.querySelector('button[onclick*="generateShotPrompts"]') : null;
    const originalText = btn ? btn.textContent : '生成提示词';
    
    if (btn) {
        btn.disabled = true;
        btn.textContent = '生成中...';
    }
    
    try {
        // 获取当前分镜的索引
        const currentIndex = currentShots.findIndex(s => s.id === shotId);
        
        // 获取前序分镜描述（最多3个，按时间倒序）
        const previousShots = [];
        if (currentIndex > 0) {
            for (let i = currentIndex - 1; i >= 0 && previousShots.length < 3; i--) {
                const prevShot = currentShots[i];
                if (prevShot && prevShot.description) {
                    previousShots.push(prevShot.description);
                }
            }
        }
        
        // 获取后续分镜描述（最多3个，按时间正序）
        const nextShots = [];
        if (currentIndex >= 0 && currentIndex < currentShots.length - 1) {
            for (let i = currentIndex + 1; i < currentShots.length && nextShots.length < 3; i++) {
                const nextShot = currentShots[i];
                if (nextShot && nextShot.description) {
                    nextShots.push(nextShot.description);
                }
            }
        }
        
        // 调用生成分镜提示词工具
        const formData = new FormData();
        formData.append('shot_description', description);
        formData.append('duration', duration.toString());
        formData.append('related_materials', JSON.stringify(relatedMaterials));
        formData.append('previous_shots', JSON.stringify(previousShots));
        formData.append('next_shots', JSON.stringify(nextShots));
        
        const result = await API.createToolTask('generate_shot_prompts', formData);
        const taskId = result.task_id;
        
        // 轮询任务状态
        let pollCount = 0;
        const maxPolls = 150;
        const pollInterval = setInterval(async () => {
            pollCount++;
            if (pollCount > maxPolls) {
                clearInterval(pollInterval);
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = originalText;
                }
                await showAlertDialog('生成超时，请稍后查看历史记录', '提示');
                return;
            }
            
            try {
                const status = await API.getTaskStatus(taskId);
                if (status.status === 'success') {
                    clearInterval(pollInterval);
                    const taskResult = await API.getTaskResult(taskId);
                    const promptsText = taskResult.output.text || '';
                    
                    // 解析提示词
                    if (window.parseShotPrompts) {
                        const parsed = window.parseShotPrompts(promptsText);
                        
                        // 填充到对应字段
                        shot.image_prompt = parsed.image_prompt || shot.image_prompt || '';
                        shot.video_prompt = parsed.video_prompt || shot.video_prompt || '';
                        shot.reference_video_prompt = parsed.reference_video_prompt || shot.reference_video_prompt || '';
                        shot.audio_prompt = parsed.audio_prompt || shot.audio_prompt || '';
                        shot.dialogue_prompt = parsed.dialogue_prompt || shot.dialogue_prompt || '';
                        
                        // 保存到后端
                        await API.updateShot(
                            workId, episodeId, shotId,
                            null,
                            shot.image_prompt,
                            shot.video_prompt,
                            shot.audio_prompt,
                            null,
                            shot.reference_video_prompt,
                            shot.dialogue_prompt
                        );
                        
                        // 重新渲染分镜卡片
                        renderShots();
                        
                        await showAlertDialog('提示词生成成功', '成功');
                    } else {
                        await showAlertDialog('解析提示词失败', '错误');
                    }
                    
                    // 恢复按钮状态（已重新渲染，不需要手动恢复）
                } else if (status.status === 'failed') {
                    clearInterval(pollInterval);
                    if (btn) {
                        btn.disabled = false;
                        btn.textContent = originalText;
                    }
                    await showAlertDialog('生成提示词失败: ' + (status.error || '未知错误'), '错误');
                }
            } catch (error) {
                console.error('轮询任务状态失败:', error);
            }
        }, 2000);
        
    } catch (error) {
        console.error('生成提示词失败:', error);
        if (btn) {
            btn.disabled = false;
            btn.textContent = originalText;
        }
        await showAlertDialog('生成提示词失败: ' + error.message, '错误');
    }
}

// 生成全部分镜提示词
let generateAllPromptsCooldown = 0; // 倒计时剩余秒数
let generateAllPromptsTimer = null; // 倒计时定时器

async function generateAllShotPrompts() {
    // 检查倒计时
    if (generateAllPromptsCooldown > 0) {
        await showAlertDialog(`请等待 ${generateAllPromptsCooldown} 秒后再试`, '提示');
        return;
    }
    
    if (!currentShots || currentShots.length === 0) {
        await showAlertDialog('没有可生成提示词的分镜', '提示');
        return;
    }
    
    const confirmed = await showConfirmDialog(
        `确定要为所有 ${currentShots.length} 个分镜生成提示词吗？`,
        '确认生成'
    );
    
    if (!confirmed) {
        return;
    }
    
    const btn = document.getElementById('generate-all-prompts-btn');
    btn.disabled = true;
    
    // 开始倒计时
    generateAllPromptsCooldown = 30;
    updateGenerateAllPromptsButton();
    
    if (generateAllPromptsTimer) {
        clearInterval(generateAllPromptsTimer);
    }
    
    generateAllPromptsTimer = setInterval(() => {
        generateAllPromptsCooldown--;
        updateGenerateAllPromptsButton();
        
        if (generateAllPromptsCooldown <= 0) {
            clearInterval(generateAllPromptsTimer);
            generateAllPromptsTimer = null;
            btn.disabled = false;
            btn.textContent = '生成全部分镜提示词';
        }
    }, 1000);
    
    // 遍历所有分镜，依次生成提示词
    let successCount = 0;
    let failCount = 0;
    
    for (const shot of currentShots) {
        try {
            // 检查分镜是否有描述
            if (!shot.description || !shot.description.trim()) {
                console.warn(`分镜 ${shot.id} 没有描述，跳过`);
                failCount++;
                continue;
            }
            
            // 调用生成提示词函数
            await generateShotPrompts(shot.id);
            successCount++;
            
            // 每个分镜之间稍微延迟，避免请求过于频繁
            await new Promise(resolve => setTimeout(resolve, 500));
        } catch (error) {
            console.error(`为分镜 ${shot.id} 生成提示词失败:`, error);
            failCount++;
        }
    }
    
    // 显示结果
    if (failCount === 0) {
        await showAlertDialog(`成功为 ${successCount} 个分镜生成提示词`, '成功');
    } else {
        await showAlertDialog(`完成：成功 ${successCount} 个，失败 ${failCount} 个`, '完成');
    }
}

// 更新"生成全部分镜提示词"按钮文本
function updateGenerateAllPromptsButton() {
    const btn = document.getElementById('generate-all-prompts-btn');
    if (!btn) return;
    
    if (generateAllPromptsCooldown > 0) {
        btn.textContent = `生成全部分镜提示词 (${generateAllPromptsCooldown}秒)`;
    } else {
        btn.textContent = '生成全部分镜提示词';
    }
}

// 生成参考视频
async function generateReferenceVideo(shotId) {
    const shot = currentShots.find(s => s.id === shotId);
    if (!shot) return;
    
    const prompt = shot.reference_video_prompt || shot.video_prompt || '';
    const duration = shot.duration || 5;
    const relatedMaterials = shot.related_materials || [];
    
    if (!prompt.trim()) {
        await showAlertDialog('请先填写参考视频提示词', '提示');
        return;
    }
    
    if (relatedMaterials.length === 0) {
        await showAlertDialog('请先关联素材', '提示');
        return;
    }
    
    // 获取按钮并更新状态
    const card = document.querySelector(`[data-shot-id="${shotId}"]`);
    const referenceTab = card ? document.getElementById(`${shotId}-reference-prompt`) : null;
    const btn = referenceTab ? referenceTab.querySelector('button[onclick*="generateReferenceVideo"]') : null;
    const originalText = btn ? btn.textContent : '生成视频';
    
    if (btn) {
        btn.disabled = true;
        btn.textContent = '生成中...';
    }
    
    try {
        // 获取作品的比例
        const work = await API.getWork(workId);
        const aspectRatio = work.aspect_ratio || '16:9';
        
        // 获取素材的主图并转换为File对象
        const imageFiles = [];
        for (const materialName of relatedMaterials) {
            // 查找素材
            const allMaterialIds = [
                ...(work.character_materials || []).map(id => ({id, type: 'characters'})),
                ...(work.scene_materials || []).map(id => ({id, type: 'scenes'})),
                ...(work.prop_materials || []).map(id => ({id, type: 'props'}))
            ];
            
            for (const {id, type} of allMaterialIds) {
                try {
                    const material = await API.getMaterial(type, id);
                    if (material && material.name === materialName && material.main_image) {
                        // 获取图片并转换为File对象
                        const imageUrl = `http://localhost:8000/api/materials/${type}/${id}/image/${material.main_image}`;
                        try {
                            const imageResponse = await fetch(imageUrl);
                            const imageBlob = await imageResponse.blob();
                            const imageFile = new File([imageBlob], `${material.main_image}`, { type: 'image/jpeg' });
                            imageFiles.push(imageFile);
                        } catch (fetchError) {
                            console.error('获取素材图片失败:', fetchError);
                        }
                        break;
                    }
                } catch (error) {
                    continue;
                }
            }
        }
        
        if (imageFiles.length === 0) {
            await showAlertDialog('无法获取素材图片', '错误');
            return;
        }
        
        // 调用vidu参考生视频工具
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('aspect_ratio', aspectRatio);
        formData.append('resolution', '720p');
        formData.append('duration', duration.toString());
        
        // 添加图片文件（后端会上传到OSS）
        for (const file of imageFiles) {
            formData.append('images', file);
        }
        
        const result = await API.createToolTask('vidu_ref_image_to_video', formData);
        const taskId = result.task_id;
        
        // 保存任务ID到分镜
        shot.video_task_id = taskId;
        await API.updateShot(workId, episodeId, shotId, null, null, null, null, null, null, null, taskId);
        
        // 开始轮询任务状态
        let pollCount = 0;
        const maxPolls = 150;
        const pollInterval = setInterval(async () => {
            pollCount++;
            if (pollCount > maxPolls) {
                clearInterval(pollInterval);
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = originalText;
                }
                await showAlertDialog('生成超时，请稍后查看历史记录', '提示');
                return;
            }
            
            try {
                const status = await API.getTaskStatus(taskId);
                if (status.status === 'success') {
                    clearInterval(pollInterval);
                    const taskResult = await API.getTaskResult(taskId);
                    let videoUrl = taskResult.output.video_url || '';
                    
                    if (videoUrl) {
                        // 如果是外部URL，下载到本地
                        if (videoUrl.startsWith('http')) {
                            try {
                                const downloadResult = await API.downloadVideoToShot(workId, episodeId, shotId, videoUrl);
                                videoUrl = downloadResult.url;
                            } catch (error) {
                                console.error('下载视频失败:', error);
                                // 如果下载失败，继续使用原始URL
                            }
                        }
                        
                        // 保存视频URL到分镜
                        shot.current_video = videoUrl;
                        if (!shot.video_history) {
                            shot.video_history = [];
                        }
                        shot.video_history.push({
                            video_path: videoUrl,
                            generated_at: new Date().toISOString()
                        });
                        shot.video_task_id = null;
                        
                        await API.updateShot(workId, episodeId, shotId, null, null, null, null, null, null, null, null, videoUrl, JSON.stringify(shot.video_history));
                        
                        // 重新渲染分镜卡片
                        renderShots();
                        
                        await showAlertDialog('参考视频生成成功', '成功');
                    }
                    
                    // 恢复按钮状态（已重新渲染，不需要手动恢复）
                } else if (status.status === 'failed') {
                    clearInterval(pollInterval);
                    shot.video_task_id = null;
                    if (btn) {
                        btn.disabled = false;
                        btn.textContent = originalText;
                    }
                    await showAlertDialog('生成参考视频失败: ' + (status.error || '未知错误'), '错误');
                }
            } catch (error) {
                console.error('轮询任务状态失败:', error);
            }
        }, 2000);
        
    } catch (error) {
        console.error('生成参考视频失败:', error);
        if (btn) {
            btn.disabled = false;
            btn.textContent = originalText;
        }
        await showAlertDialog('生成参考视频失败: ' + error.message, '错误');
    }
}

// 显示参考视频历史
function showReferenceVideoHistory(shotId) {
    const shot = currentShots.find(s => s.id === shotId);
    if (!shot || !shot.video_history || shot.video_history.length === 0) {
        showAlertDialog('暂无历史视频', '提示');
        return;
    }
    
    // 先关闭并移除已存在的 dialog
    const existingDialog = document.getElementById(`reference-video-history-dialog-${shotId}`);
    if (existingDialog) {
        existingDialog.close();
        existingDialog.remove();
    }
    
    // 规范化路径用于比较（移除开头的斜杠和协议）
    const normalizePath = (path) => {
        if (!path) return '';
        // 移除 http:// 或 https://
        path = path.replace(/^https?:\/\/[^\/]+/, '');
        // 移除开头的斜杠
        path = path.replace(/^\/+/, '');
        return path;
    };
    
    // 确定当前视频：如果有 current_video 就用它，否则如果只有一个视频，就认为它是当前视频（仅显示逻辑）
    const effectiveCurrentVideo = shot.current_video || (shot.video_history.length === 1 ? shot.video_history[0].video_path : null);
    const currentVideoNormalized = normalizePath(effectiveCurrentVideo);
    
    // 创建历史列表（使用按钮）
    const historyList = shot.video_history.map((item, index) => {
        const itemPathNormalized = normalizePath(item.video_path);
        // 如果只有一个视频且没有 current_video，或者路径匹配，则认为是当前视频
        const isCurrent = currentVideoNormalized && currentVideoNormalized === itemPathNormalized;
        const escapedPath = escapeHtml(item.video_path).replace(/'/g, "&#39;");
        return `
            <button class="btn btn-secondary video-history-item ${isCurrent ? 'current' : ''}" 
                    data-video-path="${escapeHtml(item.video_path)}"
                    onclick="selectReferenceVideo('${shotId}', '${escapedPath}', this)"
                    style="width: 100%; margin-bottom: 0.5rem; text-align: left; display: flex; justify-content: space-between; align-items: center;">
                <span>视频 ${index + 1}</span>
                ${isCurrent ? '<span class="badge">当前</span>' : ''}
            </button>
        `;
    }).join('');
    
    // 创建历史面板（使用dialog）
    const dialog = document.createElement('dialog');
    dialog.id = `reference-video-history-dialog-${shotId}`;
    dialog.className = 'modal';
    dialog.innerHTML = `
        <div class="modal-content" style="max-width: 800px;">
            <div class="modal-header">
                <h3>参考视频历史</h3>
                <button class="modal-close" onclick="closeReferenceVideoHistory('${shotId}')">&times;</button>
            </div>
            <div style="display: flex; gap: 1rem;">
                <div style="flex: 1;">
                    <h4>历史列表</h4>
                    <div id="reference-video-history-list-${shotId}" style="display: flex; flex-direction: column;">
                        ${historyList}
                    </div>
                </div>
                <div style="flex: 1;">
                    <h4>预览</h4>
                    <div id="reference-video-preview-${shotId}">
                        <video id="reference-video-player-${shotId}" controls style="width: 100%;"></video>
                    </div>
                </div>
            </div>
            <div class="modal-footer" style="margin-top: 1rem;">
                <button class="btn btn-primary" onclick="confirmReferenceVideoChange('${shotId}')">更改</button>
                <button class="btn btn-secondary" onclick="closeReferenceVideoHistory('${shotId}')">关闭</button>
            </div>
        </div>
    `;
    document.body.appendChild(dialog);
    dialog.showModal();
    
    // 监听关闭事件，确保清理
    dialog.addEventListener('close', () => {
        const videoPlayer = document.getElementById(`reference-video-player-${shotId}`);
        if (videoPlayer) {
            videoPlayer.src = '';
            videoPlayer.load();
        }
    });
    
    // 设置当前选中的视频（使用有效当前视频）
    const defaultVideo = effectiveCurrentVideo;
    window.currentReferenceVideoSelection = {
        shotId: shotId,
        videoPath: defaultVideo
    };
    
    // 确保当前视频的按钮被正确选中（添加 current 类）
    setTimeout(() => {
        const historyListElement = document.getElementById(`reference-video-history-list-${shotId}`);
        if (historyListElement && defaultVideo) {
            const defaultVideoNormalized = normalizePath(defaultVideo);
            historyListElement.querySelectorAll('.video-history-item').forEach(btn => {
                const btnPath = normalizePath(btn.getAttribute('data-video-path'));
                if (btnPath === defaultVideoNormalized) {
                    btn.classList.add('current');
                    // 更新按钮内容，添加"当前"标记（如果还没有）
                    const badge = btn.querySelector('.badge');
                    if (!badge) {
                        const span = document.createElement('span');
                        span.className = 'badge';
                        span.textContent = '当前';
                        btn.appendChild(span);
                    }
                } else {
                    btn.classList.remove('current');
                    const badge = btn.querySelector('.badge');
                    if (badge) {
                        badge.remove();
                    }
                }
            });
        }
    }, 0);
    
    // 加载默认视频预览（优先加载当前视频）
    if (defaultVideo) {
        const videoPlayer = document.getElementById(`reference-video-player-${shotId}`);
        if (videoPlayer) {
            const videoUrl = defaultVideo.startsWith('http') ? defaultVideo : `http://localhost:8000${defaultVideo}`;
            videoPlayer.src = videoUrl;
            videoPlayer.load();
        }
    }
}

// 关闭参考视频历史对话框
function closeReferenceVideoHistory(shotId) {
    const dialog = document.getElementById(`reference-video-history-dialog-${shotId}`);
    if (dialog) {
        const videoPlayer = document.getElementById(`reference-video-player-${shotId}`);
        if (videoPlayer) {
            videoPlayer.src = '';
            videoPlayer.load();
        }
        dialog.close();
        dialog.remove();
    }
}

// 选择参考视频
function selectReferenceVideo(shotId, videoPath, buttonElement) {
    window.currentReferenceVideoSelection = {
        shotId: shotId,
        videoPath: videoPath
    };
    
    // 更新预览
    const videoPlayer = document.getElementById(`reference-video-player-${shotId}`);
    if (videoPlayer) {
        const videoUrl = videoPath.startsWith('http') ? videoPath : `http://localhost:8000${videoPath}`;
        videoPlayer.src = videoUrl;
        videoPlayer.load();
    }
    
    // 更新选中状态
    const historyList = document.getElementById(`reference-video-history-list-${shotId}`);
    if (historyList) {
        historyList.querySelectorAll('.video-history-item').forEach(item => {
            item.classList.remove('current');
        });
        if (buttonElement) {
            buttonElement.classList.add('current');
        }
    }
}

// 确认更改参考视频
async function confirmReferenceVideoChange(shotId) {
    const selection = window.currentReferenceVideoSelection;
    if (!selection || selection.shotId !== shotId) {
        await showAlertDialog('请先选择一个视频', '提示');
        return;
    }
    
    const shot = currentShots.find(s => s.id === shotId);
    if (!shot) return;
    
    try {
        shot.current_video = selection.videoPath;
        await API.updateShot(workId, episodeId, shotId, null, null, null, null, null, null, null, null, selection.videoPath, JSON.stringify(shot.video_history || []));
        
        // 重新渲染分镜卡片
        renderShots();
        
        // 关闭对话框
        closeReferenceVideoHistory(shotId);
        
        await showAlertDialog('参考视频已更改', '成功');
    } catch (error) {
        console.error('更改参考视频失败:', error);
        await showAlertDialog('更改参考视频失败: ' + error.message, '错误');
    }
}

// 渲染参考视频内容
function renderReferenceVideoContent(shot) {
    if (shot.current_video) {
        const videoUrl = shot.current_video.startsWith('http') ? shot.current_video : `http://localhost:8000${shot.current_video}`;
        return `<video controls src="${videoUrl}" style="width: 100%; max-height: 500px;"></video>`;
    } else if (shot.video_task_id) {
        return `<div class="loading">视频生成中...</div>`;
    } else {
        return `<div class="empty-content">暂无参考视频</div>`;
    }
}

// 将 parseShotPrompts 函数暴露为全局函数
window.parseShotPrompts = function(text) {
    const lines = text.split('\n').map(l => l.trim()).filter(l => l);
    const result = {
        image_prompt: '',
        video_prompt: '',
        reference_video_prompt: '',
        audio_prompt: '',
        dialogue_prompt: ''
    };
    
    let currentPrompt = null;
    for (const line of lines) {
        if (line.startsWith('分镜图片提示词:')) {
            currentPrompt = 'image_prompt';
            result.image_prompt = line.replace('分镜图片提示词:', '').trim();
        } else if (line.startsWith('分镜视频提示词:')) {
            currentPrompt = 'video_prompt';
            result.video_prompt = line.replace('分镜视频提示词:', '').trim();
        } else if (line.startsWith('参考视频提示词:')) {
            currentPrompt = 'reference_video_prompt';
            result.reference_video_prompt = line.replace('参考视频提示词:', '').trim();
        } else if (line.startsWith('音频提示词:')) {
            currentPrompt = 'audio_prompt';
            result.audio_prompt = line.replace('音频提示词:', '').trim();
        } else if (line.startsWith('台词提示词:')) {
            currentPrompt = 'dialogue_prompt';
            result.dialogue_prompt = line.replace('台词提示词:', '').trim();
        } else if (currentPrompt && line) {
            // 续行
            result[currentPrompt] += '\n' + line;
        }
    }
    
    return result;
};

function closePreview() {
    const modal = document.getElementById('preview-modal');
    modal.close();
}
