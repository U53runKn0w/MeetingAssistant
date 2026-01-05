import {defineStore} from 'pinia';

export const useMessageStore = defineStore('message', {
    state: () => ({
        messages: [] // 存储消息对象：{ id, text, type }
    }),
    actions: {
        // 通用添加方法
        addMessage(text, type = 'danger') {
            const id = Date.now() + Math.random(); // 确保 ID 唯一
            this.messages.push({id, text, type});

            // 自动移除
            setTimeout(() => {
                this.removeMessage(id);
            }, 5000);
        },

        // 快捷方式：保持 setError 兼容旧代码
        setError(msg) {
            this.addMessage(msg, 'danger');
        },
        setSuccess(msg) {
            this.addMessage(msg, 'success');
        },
        setWarning(msg) {
            this.addMessage(msg, 'warning');
        },
        setInfo(msg) {
            this.addMessage(msg, 'info');
        },

        removeMessage(id) {
            this.messages = this.messages.filter(m => m.id !== id);
        },
        // 新增：清空所有消息
        clearAll() {
            this.messages = [];
        }
    }
});