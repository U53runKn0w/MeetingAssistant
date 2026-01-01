<template>
  <div class="chat-container">
    <div class="messages">
      <div v-for="(msg, index) in messages" :key="index" :class="['msg', msg.role]">
        <div v-if="msg.role === 'tool'" class="tool-info">🔧 {{ msg.content }}</div>
        <pre v-else>{{ msg.content }}</pre>
      </div>
    </div>

    <div class="input-area">
      <input v-model="userInput" @keyup.enter="sendMessage" placeholder="输入问题..." />
      <button @click="sendMessage" :disabled="isStreaming">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const messages = ref([]);
const userInput = ref('');
const isStreaming = ref(false);

const sendMessage = () => {
  if (!userInput.value || isStreaming.value) return;

  const query = userInput.value;
  // 先把用户的问题加入列表
  messages.value.push({ role: 'user', content: query });
  // 初始化一条空的 AI 回复记录
  messages.value.push({ role: 'assistant', content: '' });

  const aiMsgIndex = messages.value.length - 1;
  isStreaming.value = true;

  // 1. 创建 EventSource 连接后端 Flask 接口
  const url = `http://localhost:5000/api/chat?query=${encodeURIComponent(query)}`;
  const eventSource = new EventSource(url);

  // 2. 监听消息
  eventSource.onmessage = (event) => {
    // 检查结束标志
    if (event.data === "[DONE]") {
      eventSource.close();
      isStreaming.value = false;
      return;
    }

    try {
      const payload = JSON.parse(event.data);

      if (payload.type === 'content') {
        // 实时追加内容到最后一条消息
        messages.value[aiMsgIndex].content += payload.data;
      } else if (payload.type === 'tool_start') {
        // 可选：在界面展示工具调用状态
        console.log("Tool starting:", payload.data);
      }
    } catch (e) {
      console.error("解析错误:", e);
    }
  };

  // 3. 错误处理
  eventSource.onerror = (err) => {
    console.error("SSE 异常中断:", err);
    eventSource.close();
    isStreaming.value = false;
  };

  userInput.value = '';
};
</script>

<style scoped>
.messages { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; }
.msg { margin-bottom: 10px; }
.tool-info { font-size: 12px; color: #666; font-style: italic; }
pre { white-space: pre-wrap; word-wrap: break-word; font-family: inherit; }
</style>