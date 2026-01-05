<template>
  <!--  <nav>-->
  <!--    <router-link to="/">主页</router-link> |-->
  <!--    <router-link to="/result">结果</router-link> |-->
  <!--    <router-link to="/login">登录</router-link>-->
  <!--  </nav>-->
  <div class="position-fixed top-0 start-50 translate-middle-x p-3">
    <div class="toast align-items-center text-white bg-danger border-0"
         :class="{ show: errorStore.show }"
         role="alert">
      <div class="d-flex">
        <div class="toast-body">
          {{ errorStore.message }}
        </div>
        <button @click="errorStore.clearError" type="button" class="btn-close btn-close-white me-2 m-auto"></button>
      </div>
    </div>
  </div>
  <router-view></router-view>
</template>

<script setup>
import {useErrorStore} from "@/store/error.js";
const errorStore = useErrorStore();
</script>