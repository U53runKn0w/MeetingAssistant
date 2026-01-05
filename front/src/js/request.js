import axios from 'axios';
import router from "@/router/index.js";

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
        // Axios 默认认为 2xx 状态码是成功
        // 如果你的后端在 200 内部定义了业务错误码（如 {code: 500, msg: "失败"}）
        const res = response.data;

        // 这里假设后端返回的结构中包含业务 code
        if (res.code && res.code !== 200) {
            // 处理特定的业务错误
            return Promise.reject(new Error(res.msg || 'Error'));
        }
        return res;
    },
    async (error) => {
        // 401, 403, 500 等非 2xx 状态码会进入这里
        if (error.response) {
            const status = error.response.status;
            const data = error.response.data;

            if (status === 401) {
                // 1. 清理本地缓存
                localStorage.removeItem('token');
                // 2. 跳转到登录页（避免重复跳转逻辑可以在此处优化）
                if (router.currentRoute.value.path !== '/login') {
                    await router.push('/login');
                }
                return Promise.reject(new Error(data.msg || '身份过期，请重新登录'));
            }
        }

        console.error('Network Error:', error.message);
        return Promise.reject(error);
    }
);

export default service;