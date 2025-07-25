document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');
    const previewImage = document.getElementById('previewImage');
    const removeImage = document.getElementById('removeImage');
    const favorabilityValue = document.getElementById('favorabilityValue');

    // 自动调整文本框高度
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight < 120 ? this.scrollHeight : 120) + 'px';
    });

    // 图片上传预览
    imageUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                imagePreview.classList.remove('hidden');
            }
            reader.readAsDataURL(file);
        }
    });

    // 移除图片预览
    removeImage.addEventListener('click', function() {
        imagePreview.classList.add('hidden');
        imageUpload.value = '';
        previewImage.src = '';
    });

    // 发送消息
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
        const message = messageInput.value.trim();
        const imageFile = imageUpload.files[0];
        
        if (!message && !imageFile) {
            showNotification('请输入消息或选择图片', 'error');
            return;
        }
        // 立即添加用户消息到聊天窗口
        const messageContent = imageFile ? 
            { type: 'image', image_path: URL.createObjectURL(imageFile), content: message } : 
            messageInput.value;
        addMessageToChat(messageContent, true);
        // 禁用发送按钮防止重复提交
        sendButton.disabled = true;
        sendButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i>';

        // 创建FormData对象
        const formData = new FormData();
        if (message) formData.append('message', message);
        if (imageFile) formData.append('image', imageFile);

        // 添加正在输入提示
        const typingIndicator = createTypingIndicator();
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 发送请求
        fetch('/send_message', {
            method: 'POST',
            body: formData
        })
        .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
                }
                return response.json();
            })
        .then(data => {
            // 移除正在输入提示
            if (chatMessages.contains(typingIndicator)) {
                chatMessages.removeChild(typingIndicator);
            }

            if (data.status === 'success') {
                // 添加AI响应到聊天窗口
                const aiResponse = data.ai_response || '未能生成响应';
                addMessageToChat(aiResponse, false);
                // 清空输入框
                messageInput.value = '';
                // 清空输入
                messageInput.value = '';
                messageInput.style.height = 'auto';
                if (imageFile) {
                    imagePreview.classList.add('hidden');
                    imageUpload.value = '';
                    previewImage.src = '';
                }

                // 更新好感度
                if (data.favorability !== undefined) {
                    favorabilityValue.textContent = data.favorability;
                }

                showNotification('消息发送成功', 'success');
            } else {
                showNotification(data.message || '发送失败，请重试', 'error');
            }

            // 重新启用发送按钮
            sendButton.disabled = false;
            sendButton.innerHTML = '<i class="fa fa-paper-plane"></i>';
        })
        .catch(error => {
            // 移除正在输入提示
            if (chatMessages.contains(typingIndicator)) {
                chatMessages.removeChild(typingIndicator);
            }
            showNotification(`请求失败: ${error.message}`, 'error');
            sendButton.disabled = false;
            sendButton.innerHTML = '<i class="fa fa-paper-plane"></i>';
        });
    }

    // 创建正在输入提示
    function createTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'flex items-start space-x-3';
        div.innerHTML = `
            <div class="w-10 h-10 rounded-full bg-gradient-to-r from-pink-300 to-purple-400 flex-shrink-0"></div>
            <div class="max-w-[75%]">
                <div class="bg-gradient-to-r from-pink-100 to-purple-100 p-4 rounded-2xl shadow-sm chat-bubble-ai">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        return div;
    }

    // 添加消息到聊天窗口
    function addMessageToChat(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex items-start space-x-3 ${isUser ? 'justify-end' : ''}`;
        // 使用一致的背景色类名
        const messageClass = 'bg-gradient-to-r from-purple-900/80 to-pink-900/80 p-4 rounded-2xl shadow-lg chat-bubble-ai border border-pink-500/30 backdrop-blur-sm relative overflow-hidden before:absolute before:top-0 before:right-0 before:w-20 before:h-20 before:bg-pink-500/10 before:rounded-full before:-mr-10 before:-mt-10';
        const timestamp = new Date().toLocaleTimeString();

        // 检查是否是图片消息
        const isImageMessage = typeof content === 'object' && content.type === 'image';
        
        let messageContent = '';
        if (isImageMessage) {
            // 处理图片消息，包括图片和可能的文字内容
            messageContent = `<img src="${content.image_path}" alt="上传的图片" class="max-h-60 rounded-lg border-2 border-pink-500/50 shadow-lg">`;
            if (content.content) {
                messageContent += `<p class="text-gray-100 mt-2">${content.content}</p>`;
            }
        } else {
            messageContent = typeof content === 'string' ? content : content.content || '';
        }

        messageDiv.innerHTML = `
            ${!isUser ? `<div class="w-10 h-10 rounded-full bg-gradient-to-r from-pink-300 to-purple-400 flex-shrink-0"></div>` : ''}
            <div class="max-w-[75%]">
                <div class="${messageClass} p-4 rounded-2xl shadow-sm chat-bubble-${isUser ? 'user' : 'ai'}">
                    ${messageContent}
                </div>
                <div class="text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : ''}">${timestamp}</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 显示通知
    function showNotification(message, type = 'info') {
        // 检查是否已有通知
        let notification = document.querySelector('.custom-notification');
        if (notification) {
            notification.remove();
        }

        notification = document.createElement('div');
        notification.className = `custom-notification fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-y-10 opacity-0 ${type === 'error' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-green-50 text-green-700 border border-green-200'}`;
        notification.innerHTML = `
            <i class="fa fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'} mr-2"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(notification);

        // 显示通知
        setTimeout(() => {
            notification.classList.remove('translate-y-10', 'opacity-0');
        }, 10);

        // 3秒后隐藏
        setTimeout(() => {
            notification.classList.add('translate-y-10', 'opacity-0');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
});