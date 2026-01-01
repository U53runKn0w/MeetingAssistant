import { createRouter, createWebHistory } from 'vue-router';
import Result from "@/views/Result.vue";
import Talk from "@/views/Talk.vue";
import Test from "@/views/Test.vue";

const routes = [
    { path: '/', component: Talk },
    { path: '/result', component: Result },
    { path: '/test', component: Test }
];

const router = createRouter({
    history: createWebHistory(), // 使用 HTML5 历史模式
    routes,
});

export default router;