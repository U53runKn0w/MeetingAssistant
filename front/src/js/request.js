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

            if (status === 401) {
                localStorage.removeItem('token');
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