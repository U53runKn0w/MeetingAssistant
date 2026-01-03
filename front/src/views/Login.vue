<template>
  <div class="container d-flex justify-content-center align-items-center" style="min-height: 100vh;">
    <div class="row w-100 justify-content-center">
      <div class="col-md-6 col-lg-4">
        <header class="text-center mb-4">
          <div class="d-inline-block p-3 bg-primary bg-opacity-10 rounded-circle mb-3">
            <i class="bi bi-robot text-primary display-4"></i>
          </div>
          <h1 class="h3 fw-bold text-primary">会议助手</h1>
          <p class="text-muted">欢迎回来，请登录您的账户</p>
        </header>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4 p-md-5">
            <form @submit.prevent="handleLogin">
              <div v-if="errorMessage" class="alert alert-danger py-2 small mb-3">
                <i class="bi bi-exclamation-circle me-2"></i>{{ errorMessage }}
              </div>

              <div class="mb-3">
                <label class="form-label small fw-bold text-secondary">账号</label>
                <div class="input-group">
                  <span class="input-group-text bg-light border-end-0">
                    <i class="bi bi-envelope text-muted"></i>
                  </span>
                  <input
                      v-model="loginForm.username"
                      type="text"
                      class="form-control bg-light border-start-0"
                      placeholder="请输入您的账号"
                      required
                  >
                </div>
              </div>

              <div class="mb-3">
                <div class="d-flex justify-content-between">
                  <label class="form-label small fw-bold text-secondary">密码</label>
                  <a href="#" class="small text-decoration-none">忘记密码？</a>
                </div>
                <div class="input-group">
                  <span class="input-group-text bg-light border-end-0">
                    <i class="bi bi-lock text-muted"></i>
                  </span>
                  <input
                      v-model="loginForm.password"
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control bg-light border-start-0"
                      placeholder="请输入您的密码"
                      required
                  >
                  <button
                      class="btn btn-outline-light border border-start-0 text-muted"
                      type="button"
                      @click="showPassword = !showPassword"
                  >
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
              </div>

              <div class="mb-4 form-check">
                <input type="checkbox" class="form-check-input" id="rememberMe" v-model="loginForm.remember">
                <label class="form-check-label small text-muted" for="rememberMe">保持登录状态</label>
              </div>

              <button
                  type="submit"
                  class="btn btn-primary w-100 py-2 fw-bold"
                  :disabled="isSubmitting"
              >
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-box-arrow-in-right me-2"></i>
                {{ isSubmitting ? '登录中...' : '立即登录' }}
              </button>
            </form>

            <div class="text-center mt-4">
              <p class="small text-muted position-relative">
                <span class="bg-white px-2">或者通过以下方式</span>
              </p>
              <div class="d-flex justify-content-center gap-2">
                <button class="btn btn-outline-light border text-dark shadow-xs px-3">
                  <i class="bi bi-wechat text-success me-2"></i>微信
                </button>
                <button class="btn btn-outline-light border text-dark shadow-xs px-3">
                  <i class="bi bi-github me-2"></i>GitHub
                </button>
              </div>
            </div>
          </div>
        </div>

        <p class="text-center mt-4 text-muted small">
          还没有账号？ <a href="#" class="fw-bold text-primary text-decoration-none">立即注册</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive} from 'vue';
import service from "@/js/request.js";
import router from "@/router/index.js";

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
});

const isSubmitting = ref(false);
const showPassword = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
  isSubmitting.value = true;
  errorMessage.value = '';

  service.post('/login', {
    username: loginForm.username,
    password: loginForm.password,
  }).then(response => {
    localStorage.setItem('token', response.access_token);
    router.push('/');
  }).catch(error => {
    console.log(error);
    errorMessage.value = '账号或密码错误，请检查后重试。';
  }).finally(() => {
    isSubmitting.value = false;
  })
};
</script>

<style scoped>
/* 增强 UI 细节 */
.card {
  border-radius: 1rem;
}

.input-group-text {
  border-color: #dee2e6;
}

.form-control:focus {
  background-color: #fff !important;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.15);
}

.btn-primary {
  padding-top: 0.6rem;
  padding-bottom: 0.6rem;
  border-radius: 0.5rem;
}

/* 装饰性水平线 */
p.position-relative::before {
  content: "";
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #eee;
  z-index: -1;
}
</style>