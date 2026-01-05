<template>
  <!--  <nav class="navbar">-->
  <!--    <div class="nav-links">-->
  <!--      <router-link to="/" class="nav-item">主页</router-link>-->
  <!--      <router-link to="/result" class="nav-item">结果</router-link>-->
  <!--      <router-link to="/login" class="nav-item login-btn">登录</router-link>-->
  <!--    </div>-->
  <!--  </nav>-->

  <div class="toast-container position-fixed top-0 end-0 p-3">
    <div
        v-for="msg in messageStore.messages"
        :key="msg.id"
        class="toast show align-items-center border-0 mb-2"
        :class="[`text-white bg-${msg.type}`]"
        role="alert"
    >
      <div class="d-flex">
        <div class="toast-body">
          <span v-if="msg.type === 'success'">✅ </span>
          <span v-if="msg.type === 'danger'">❌ </span>
          <span v-if="msg.type === 'warning'">⚠️ </span>
          {{ msg.text }}
        </div>
        <button
            @click="messageStore.removeMessage(msg.id)"
            type="button"
            class="btn-close btn-close-white me-2 m-auto"
        ></button>
      </div>
    </div>
  </div>
  <router-view></router-view>
</template>

<script setup>
import {useMessageStore} from "@/store/error.js";
import {onUnmounted} from "vue";
import router from "@/router/index.js";

const messageStore = useMessageStore();

// 注册全局后置守卫：每次路由跳转完成后执行
const unregister = router.afterEach(() => {
  messageStore.clearAll();
});

onUnmounted(() => {
  unregister();
});

</script>

<style scoped>
.toast {
  transition: all 0.3s ease;
  display: flex !important;
}

/* 导航栏容器 */
.navbar {
  background-color: #ffffff;
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center; /* 居中对齐，也可以改为 flex-start */
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 20px; /* 链接之间的间距 */
}

/* 基础链接样式 */
.nav-item {
  text-decoration: none;
  color: #2c3e50;
  font-weight: 500;
  padding: 8px 12px;
  transition: all 0.3s ease;
  border-radius: 6px;
}

/* 悬停效果 */
.nav-item:hover {
  color: #42b983;
  background-color: #f0fdf4;
}

/* Vue Router 激活状态的样式 */
.router-link-active {
  color: #42b983;
  font-weight: bold;
  border-bottom: 2px solid #42b983;
  border-radius: 0; /* 激活时去掉圆角以配合底边框 */
}

/* 特殊样式的登录按钮 */
.login-btn {
  background-color: #42b983;
  color: white !important;
  margin-left: 10px;
}

.login-btn:hover {
  background-color: #3aa876;
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.3);
}
</style>