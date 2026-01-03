import { createRouter, createWebHistory } from 'vue-router';
import Result from "@/views/Result.vue";
import Talk from "@/views/Talk.vue";
import Login from "@/views/Login.vue";

const routes = [
    { path: '/', component: Talk },
    { path: '/result', component: Result },
    { path: '/login', component: Login }
];

const router = createRouter({
    history: createWebHistory(), // 使用 HTML5 历史模式
    routes,
});

export default router;