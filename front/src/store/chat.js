import {defineStore} from 'pinia'
import {dummyMeeting} from "@/js/etc.js";
import {parseReActContent} from "@/js/util.js";

export const useChat = defineStore('chat', {
    state: () => ({
        messages: [],
        question: '',
        meeting: dummyMeeting,
        buttonsShow: false
    }),
    actions: {
        // 根据后端返回的历史记录还原聊天
        setMessagesFromHistory(conversations) {
            this.messages = [];
            if (!conversations) return;

            conversations.forEach(conv => {
                if (conv.role === 'user') {
                    // 构造用户消息格式
                    this.messages.push({
                        type: 'UserQuestion', // 自定义一个类型给用户问题
                        text: conv.content
                    });
                } else if (conv.role === 'assistant') {
                    // 这里的 content 是 AI 的完整 ReAct 过程字符串
                    // 我们利用 util.js 里的 parseReActContent 再次解析它
                    const segments = parseReActContent(conv.content);
                    this.messages.push(...segments);
                }
            });

            // 如果最后一条是 Final Answer，显示按钮
            const lastMsg = this.messages[this.messages.length - 1];
            if (lastMsg && lastMsg.type === 'Final Answer') {
                this.buttonsShow = true;
            } else {
                this.buttonsShow = false;
            }
        },
        extractObservation() {
            let actionObservation = {}
            let current;
            this.messages.forEach((item) => {
                if (item.type === "Action") {
                    current = item.text;
                } else if (item.type === "Observation") {
                    actionObservation[current] = item.text;
                }
            })
            return actionObservation;
        }
    },
})