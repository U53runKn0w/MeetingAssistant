import axios from 'axios';

const service = axios.create({
    baseURL: import.meta.env.VITE_APP_BASE_API, // 从环境变量获取
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
        const {code, msg, data} = response.data;

        if (code === 200) return data;

        if (code === 401) {
            // 执行登出、跳转逻辑
        }

        return Promise.reject(new Error(msg || 'Error'));
    },
    (error) => {
        // 处理 HTTP 状态码（404, 500 等）
        console.error('Network Error:', error.message);
        return Promise.reject(error);
    }
);

export default service;