/**
 * API 客户端
 */

const API_BASE = 'http://localhost:8000/api';

class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...options.headers,
            }
        };
        
        // 如果是 FormData，不要设置 Content-Type，让浏览器自动设置（包含 boundary）
        if (options.body instanceof FormData) {
            delete config.headers['Content-Type'];
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                // 尝试获取更详细的错误信息
                const errorDetail = data.detail || data.message || JSON.stringify(data);
                console.error('API Error Detail:', errorDetail);
                throw new Error(errorDetail);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // 素材管理 API
    static async listMaterials(type) {
        return this.request(`/materials/${type}`);
    }

    static async getMaterial(type, id) {
        return this.request(`/materials/${type}/${id}`);
    }

    static async createMaterial(type, formData) {
        return this.request(`/materials/${type}`, {
            method: 'POST',
            body: formData
        });
    }

    static async updateMaterial(type, id, formData) {
        return this.request(`/materials/${type}/${id}`, {
            method: 'PUT',
            body: formData
        });
    }

    static async deleteMaterial(type, id) {
        return this.request(`/materials/${type}/${id}`, {
            method: 'DELETE'
        });
    }

    // 风格管理 API
    static async getStyles() {
        return this.request(`/styles`);
    }

    static async getStyle(id) {
        return this.request(`/styles/${id}`);
    }

    static async createStyle(formData) {
        return this.request(`/styles`, {
            method: 'POST',
            body: formData
        });
    }

    static async updateStyle(id, formData) {
        return this.request(`/styles/${id}`, {
            method: 'PUT',
            body: formData
        });
    }

    static async deleteStyle(id) {
        return this.request(`/styles/${id}`, {
            method: 'DELETE'
        });
    }

    // 作品管理 API
    static async listWorks() {
        return this.request('/works');
    }

    static async getWork(id) {
        return this.request(`/works/${id}`);
    }

    static async createWork(formData) {
        return this.request('/works', {
            method: 'POST',
            body: formData
        });
    }

    static async updateWork(id, formData) {
        return this.request(`/works/${id}`, {
            method: 'PUT',
            body: formData
        });
    }

    static async deleteWork(id) {
        return this.request(`/works/${id}`, {
            method: 'DELETE'
        });
    }

    // 剧集管理 API
    static async listEpisodes(workId) {
        return this.request(`/episodes/${workId}`);
    }

    static async getEpisode(workId, episodeId) {
        return this.request(`/episodes/${workId}/${episodeId}`);
    }

    static async createEpisode(workId, formData) {
        return this.request(`/episodes/${workId}`, {
            method: 'POST',
            body: formData
        });
    }

    static async updateEpisode(workId, episodeId, formData) {
        return this.request(`/episodes/${workId}/${episodeId}`, {
            method: 'PUT',
            body: formData
        });
    }

    static async deleteEpisode(workId, episodeId) {
        return this.request(`/episodes/${workId}/${episodeId}`, {
            method: 'DELETE'
        });
    }

    static async getScript(workId, episodeId) {
        return this.request(`/episodes/${workId}/${episodeId}/script`);
    }

    static async saveScript(workId, episodeId, script, duration, shotDuration = null) {
        const formData = new FormData();
        formData.append('script', script);
        formData.append('expected_duration', duration);
        if (shotDuration !== null) {
            formData.append('shot_duration', shotDuration);
        }
        return this.request(`/episodes/${workId}/${episodeId}/script`, {
            method: 'PUT',
            body: formData
        });
    }

    static async getStoryboard(workId, episodeId, format = null) {
        const url = `/episodes/${workId}/${episodeId}/storyboard${format ? `?format=${format}` : ''}`;
        return this.request(url);
    }

    static async saveStoryboardText(workId, episodeId, text) {
        const formData = new FormData();
        formData.append('text', text);
        return this.request(`/episodes/${workId}/${episodeId}/storyboard/text`, {
            method: 'POST',
            body: formData
        });
    }

    static async confirmStoryboard(workId, episodeId) {
        return this.request(`/content/${workId}/${episodeId}/confirm-storyboard`, {
            method: 'POST'
        });
    }

    static async updateShot(workId, episodeId, shotId, description = null, imagePrompt = null, videoPrompt = null, audioPrompt = null, duration = null, referenceVideoPrompt = null, dialoguePrompt = null, videoTaskId = null, currentVideo = null, videoHistory = null) {
        const formData = new FormData();
        if (description !== null) formData.append('description', description);
        if (imagePrompt !== null) formData.append('image_prompt', imagePrompt);
        if (videoPrompt !== null) formData.append('video_prompt', videoPrompt);
        if (audioPrompt !== null) formData.append('audio_prompt', audioPrompt);
        if (duration !== null) formData.append('duration', duration.toString());
        if (referenceVideoPrompt !== null) formData.append('reference_video_prompt', referenceVideoPrompt);
        if (dialoguePrompt !== null) formData.append('dialogue_prompt', dialoguePrompt);
        if (videoTaskId !== null) formData.append('video_task_id', videoTaskId);
        if (currentVideo !== null) formData.append('current_video', currentVideo);
        if (videoHistory !== null) formData.append('video_history', videoHistory);
        return this.request(`/content/${workId}/${episodeId}/${shotId}`, {
            method: 'PUT',
            body: formData
        });
    }

    // 内容生成 API
    static async generateStoryboard(workId, episodeId, script) {
        const formData = new FormData();
        formData.append('script', script);
        return this.request(`/content/${workId}/${episodeId}/generate-storyboard`, {
            method: 'POST',
            body: formData
        });
    }

    static async generateImages(workId, episodeId, shotId, prompt) {
        const formData = new FormData();
        formData.append('prompt', prompt);
        return this.request(`/content/${workId}/${episodeId}/${shotId}/generate-images`, {
            method: 'POST',
            body: formData
        });
    }

    static async selectImage(workId, episodeId, shotId, imagePath) {
        const formData = new FormData();
        formData.append('image_path', imagePath);
        return this.request(`/content/${workId}/${episodeId}/${shotId}/select-image`, {
            method: 'POST',
            body: formData
        });
    }

    static async generateVideo(workId, episodeId, shotId, prompt) {
        const formData = new FormData();
        formData.append('prompt', prompt);
        return this.request(`/content/${workId}/${episodeId}/${shotId}/generate-video`, {
            method: 'POST',
            body: formData
        });
    }

    static async downloadVideoToShot(workId, episodeId, shotId, videoUrl) {
        const formData = new FormData();
        formData.append('video_url', videoUrl);
        return this.request(`/content/${workId}/${episodeId}/${shotId}/download-video`, {
            method: 'POST',
            body: formData
        });
    }

    static async generateAudio(workId, episodeId, shotId, prompt) {
        const formData = new FormData();
        formData.append('prompt', prompt);
        return this.request(`/content/${workId}/${episodeId}/${shotId}/generate-audio`, {
            method: 'POST',
            body: formData
        });
    }

    static async getShot(workId, episodeId, shotId) {
        return this.request(`/content/${workId}/${episodeId}/${shotId}`);
    }

    static async updatePrompts(workId, episodeId, shotId, imagePrompt, videoPrompt, audioPrompt) {
        const formData = new FormData();
        if (imagePrompt) formData.append('image_prompt', imagePrompt);
        if (videoPrompt) formData.append('video_prompt', videoPrompt);
        if (audioPrompt) formData.append('audio_prompt', audioPrompt);
        return this.request(`/content/${workId}/${episodeId}/${shotId}/prompts`, {
            method: 'PUT',
            body: formData
        });
    }

    // 工具 API
    static async createToolTask(toolType, formData) {
        return this.request(`/tools/${toolType}/create`, {
            method: 'POST',
            body: formData
        });
    }

    static async getTaskStatus(taskId) {
        return this.request(`/tasks/${taskId}/status`);
    }

    static async getTaskResult(taskId) {
        return this.request(`/tasks/${taskId}/result`);
    }

    static async listHistory(toolType = null, page = 1, limit = 20) {
        const params = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
        if (toolType) params.append('tool_type', toolType);
        return this.request(`/tools/history?${params}`);
    }

    static async getHistoryDetail(recordId) {
        return this.request(`/tools/history/${recordId}`);
    }

    static async deleteHistory(recordId) {
        return this.request(`/tools/history/${recordId}`, {
            method: 'DELETE'
        });
    }

    static async reuseHistory(recordId) {
        return this.request(`/tools/history/${recordId}/reuse`);
    }
}

