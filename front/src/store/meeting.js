import {defineStore} from "pinia";
import {dummyMeeting} from "@/js/etc.js";
import {useChat} from "@/store/chat.js";

export const useMeeting = defineStore('meeting', {
    state: () => ({
        text: dummyMeeting,
        error: null
    }),
    actions: {
    },
})