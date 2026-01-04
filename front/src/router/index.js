import { createRouter, createWebHistory } from 'vue-router';
import ResultView from "@/views/ResultView.vue";
import HomeView from "@/views/HomeView.vue";
import LoginView from "@/views/LoginView.vue";

const routes = [
    { path: '/', component: HomeView },
    { path: '/result', component: ResultView },
    { path: '/login', component: LoginView }
];

const router = createRouter({
    history: createWebHistory(), // 使用 HTML5 历史模式
    routes,
});

export default router;