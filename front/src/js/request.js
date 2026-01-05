import axios from 'axios';
import router from "@/router/index.js";
import {useMessageStore} from "@/store/error.js";

const service = axios.create({
    baseURL: "http://localhost:5000/api",
    timeout: 5000, // 建议增加超时设置
    headers: {'Content-Type': 'application/json;charset=utf-8'}
});

service.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

service.interceptors.response.use(
    (response) => {
        const res = response.data;

        if (res.code && res.code !== 200) {
            return Promise.reject(new Error(res.msg || 'Error'));
        }
        return res;
    },
    async (error) => {
        if (error.response) {
            const status = error.response.status;
            const data = error.response.data;

            if (status === 400) {
                useMessageStore().setError(data.msg || '请求参数错误，请检查输入内容');
            } else if (status === 401) {
                localStorage.removeItem('token');
                if (router.currentRoute.value.path !== '/login') {
                    useMessageStore().setError("登录已过期，请重新登录");
                    await router.push('/login');
                }
                return Promise.reject(new Error(data.msg || '身份过期，请重新登录'));
            } else if (status === 403) {
                useMessageStore().setError('您没有权限执行此操作');
            } else if (status === 404) {
                useMessageStore().setError('请求的资源不存在，请稍后重试');
            } else if (status === 500) {
                useMessageStore().setError('服务器内部错误，请稍后重试或联系管理员');
            } else if (status >= 500) {
                useMessageStore().setError('服务器暂时不可用，请稍后重试');
            } else {
                useMessageStore().setError(data.msg || '请求失败，请稍后重试');
            }
        } else if (error.request) {
            useMessageStore().setError('网络连接失败，请检查网络设置后重试');
        } else if (error.code === 'ECONNABORTED') {
            useMessageStore().setError('请求超时，请稍后重试');
        } else {
            useMessageStore().setError('请求失败：' + (error.message || '未知错误'));
        }

        console.error('Request Error:', error);
        return Promise.reject(error);
    }
);

export default service;