/**
 * Dialog 工具函数
 * 使用 HTML5 dialog 元素实现弹窗
 */

/**
 * 显示确认对话框
 * @param {string} message - 确认消息
 * @param {string} title - 对话框标题（可选）
 * @returns {Promise<boolean>} - 用户是否确认
 */
function showConfirmDialog(message, title = '确认', type = 'default') {
    return new Promise((resolve) => {
        const dialog = document.createElement('dialog');
        dialog.className = 'confirm-dialog';
        if (type === 'danger') {
            dialog.setAttribute('data-type', 'danger');
        }
        dialog.innerHTML = `
            <div class="dialog-content">
                <div class="dialog-header">
                    <h3>${title}</h3>
                </div>
                <div class="dialog-body">
                    <p>${message}</p>
                </div>
                <div class="dialog-actions">
                    <button class="btn btn-secondary" data-action="cancel">取消</button>
                    <button class="btn btn-primary" data-action="confirm">确定</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        dialog.querySelector('[data-action="confirm"]').addEventListener('click', () => {
            dialog.close();
            document.body.removeChild(dialog);
            resolve(true);
        });
        
        dialog.querySelector('[data-action="cancel"]').addEventListener('click', () => {
            dialog.close();
            document.body.removeChild(dialog);
            resolve(false);
        });
        
        // 点击背景关闭
        dialog.addEventListener('click', (e) => {
            if (e.target === dialog) {
                dialog.close();
                document.body.removeChild(dialog);
                resolve(false);
            }
        });
        
        dialog.showModal();
    });
}

/**
 * 显示提示对话框
 * @param {string} message - 提示消息
 * @param {string} title - 对话框标题（可选）
 * @returns {Promise<void>}
 */
function showAlertDialog(message, title = '提示') {
    return new Promise((resolve) => {
        const dialog = document.createElement('dialog');
        dialog.className = 'alert-dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <div class="dialog-header">
                    <h3>${title}</h3>
                </div>
                <div class="dialog-body">
                    <p>${message}</p>
                </div>
                <div class="dialog-actions">
                    <button class="btn btn-primary" data-action="ok">确定</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        const okButton = dialog.querySelector('[data-action="ok"]');
        okButton.addEventListener('click', () => {
            dialog.close();
            document.body.removeChild(dialog);
            resolve();
        });
        
        // 点击背景关闭
        dialog.addEventListener('click', (e) => {
            if (e.target === dialog) {
                dialog.close();
                document.body.removeChild(dialog);
                resolve();
            }
        });
        
        dialog.showModal();
    });
}

