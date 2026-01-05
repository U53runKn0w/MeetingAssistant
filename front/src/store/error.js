import {defineStore} from 'pinia';

// 错误消息映射配置
const ERROR_MESSAGES = {
    network: {
        timeout: '请求超时，请检查网络连接后重试',
        failed: '网络连接失败，请检查网络设置',
        offline: '网络已断开，请检查网络连接'
    },
    auth: {
        unauthorized: '未登录或登录已过期，请重新登录',
        forbidden: '您没有权限执行此操作',
        tokenExpired: '登录已过期，请重新登录'
    },
    server: {
        internal: '服务器内部错误，请稍后重试',
        unavailable: '服务器暂时不可用，请稍后重试',
        maintenance: '系统维护中，请稍后再试'
    },
    client: {
        invalidParams: '请求参数错误，请检查输入内容',
        notFound: '请求的资源不存在',
        badRequest: '请求格式错误'
    }
};

export const useMessageStore = defineStore('message', {
    state: () => ({
        messages: [] // 存储消息对象：{ id, text, type, timestamp }
    }),
    actions: {
        // 通用添加方法
        addMessage(text, type = 'danger') {
            const id = Date.now() + Math.random(); // 确保 ID 唯一
            const timestamp = Date.now();
            this.messages.push({id, text, type, timestamp});

            // 自动移除（错误消息5秒，其他3秒）
            const duration = type === 'danger' ? 5000 : 3000;
            setTimeout(() => {
                this.removeMessage(id);
            }, duration);
        },

        // 去重的错误消息添加
        addError(text) {
            // 检查是否已存在相同的错误消息
            const exists = this.messages.some(msg =>
                msg.type === 'danger' && msg.text === text &&
                (Date.now() - msg.timestamp) < 3000 // 3秒内重复的不显示
            );

            if (!exists) {
                this.addMessage(text, 'danger');
            }
        },

        // 预定义的错误类型方法
        setNetworkError(errorType) {
            const msg = ERROR_MESSAGES.network[errorType] || ERROR_MESSAGES.network.failed;
            this.addError(msg);
        },

        setAuthError(errorType) {
            const msg = ERROR_MESSAGES.auth[errorType] || ERROR_MESSAGES.auth.unauthorized;
            this.addError(msg);
        },

        setServerError(errorType) {
            const msg = ERROR_MESSAGES.server[errorType] || ERROR_MESSAGES.server.internal;
            this.addError(msg);
        },

        setClientError(errorType) {
            const msg = ERROR_MESSAGES.client[errorType] || ERROR_MESSAGES.client.invalidParams;
            this.addError(msg);
        },

        // 快捷方式：保持 setError 兼容旧代码
        setError(msg) {
            this.addError(msg);
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