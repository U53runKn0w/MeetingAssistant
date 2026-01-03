import axios from 'axios';
import router from "@/router/index.js";

const service = axios.create({
    baseURL: "http://localhost:5000/api", // 从环境变量获取
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
    async (response) => {
        const data = response.data;
        const code = response.status;

        if (code === 200) return data;
        if (code === 401) {
            await router.push('/login');
            return data;
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