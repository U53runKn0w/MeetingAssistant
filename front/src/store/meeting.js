import {defineStore} from "pinia";
import {ref} from "vue";
import service from "@/js/request.js";
import {useChat} from "@/store/chat.js"; // 引入 Chat Store

export const useMeeting = defineStore('meeting', {
    state: () => ({
        text: "",
        error: null
    }),
    actions: {
        setMeeting(text) {
            this.text = text;
            this.currentId = null;
            // 新对话时清空消息
            const chatStore = useChat();
            chatStore.messages = [];
            chatStore.buttonsShow = false;
        },

        async loadMeeting(id) {
            try {
                this.error = null;
                const data = await service.get(`/meetings/${id}`);

                this.text = data.content || "";
                this.currentId = data.meeting_id;

                // 【关键】调用 Chat Store 还原对话
                const chatStore = useChat();
                // 注意：这里 data.conversations 是后端 manager.get_meeting 返回的
                chatStore.setMessagesFromHistory(data.conversations);

                return data;
            } catch (e) {
                throw e;
            }
        }
    },
})