<template>
  <div class="col-lg-5">
    <div class="card shadow-sm border-0 h-100">
      <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0"><i class="bi bi-journal-text me-2"></i>会议内容</h5>
        <div>
          <input
              type="file"
              ref="fileInput"
              @change="handleFileUpload"
              accept="audio/*"
              style="display: none"
          >
          <button
              @click="$refs.fileInput.click()"
              class="btn btn-sm btn-outline-primary"
              :disabled="isUploading"
          >
            <span v-if="isUploading" class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-file-earmark-music me-1"></i>
            {{ isUploading ? '转录中...' : '上传音频' }}
          </button>
        </div>
      </div>

      <div class="card-body d-flex flex-column">
        <div class="flex-grow-1">
          <label class="form-label small fw-bold text-secondary">会议纪要文本</label>
          <textarea
              v-model="meetingText"
              class="form-control"
              style="height: 400px; resize: none;"
              placeholder="在此处粘贴会议记录，或点击上方按钮上传音频自动转录..."
          ></textarea>
        </div>

        <div class="mt-3 p-2 bg-light rounded">
          <p class="small text-muted mb-0">
            <i class="bi bi-info-circle me-1"></i>
            支持直接编辑转录后的文本以修正错误。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {dummyMeeting} from "@/js/etc.js";
import {ref} from "vue";
import {storeToRefs} from "pinia";
import {useChatStore} from "@/store/chat.js";
import {useMessageStore} from "@/store/error.js";

const chatStore = useChatStore();
const {text: meetingText} = storeToRefs(chatStore);
const isUploading = ref(false);
const messageStore = useMessageStore();


const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  // 验证文件类型
  if (!file.type.startsWith('audio/')) {
    messageStore.setClientError('invalidParams');
    messageStore.setInfo('提示：请选择音频文件（mp3、wav、m4a等格式）');
    event.target.value = '';
    return;
  }

  // 验证文件大小（限制为50MB）
  const maxSize = 50 * 1024 * 1024;
  if (file.size > maxSize) {
    messageStore.setClientError('invalidParams');
    messageStore.setInfo('提示：音频文件大小不能超过50MB');
    event.target.value = '';
    return;
  }

  isUploading.value = true;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:5000/api/transcript', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    });
    const result = await response.json();

    if (result.code === 200) {
      meetingText.value = result.text;
      messageStore.setSuccess('音频转录成功');
    } else {
      messageStore.setInfo(result.message || '音频转录失败');
    }
  } catch (err) {
    console.error('音频转录失败:', err);
    messageStore.setNetworkError('failed');
    messageStore.setInfo('提示：请检查音频文件格式是否支持');
  } finally {
    isUploading.value = false;
    event.target.value = ''; // 重置 file input
  }
};
</script>

<style scoped>
code {
  word-break: break-all;
}

pre {
  background: #f1f1f1;
  padding: 10px;
  border-radius: 4px;
}

/* 优化代码块在全屏下的显示 */
.modal-body pre {
  background: #2d2d2d;
  color: #ccc;
  padding: 15px;
}

/* 确保源码查看器有手型 */
summary {
  cursor: pointer;
  outline: none;
}

/* 调整生成的 SVG 大小 */
:deep(.mermaid-viewer svg) {
  max-width: 100%;
  height: auto;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}
</style>