import {defineStore} from "pinia";
import {ref} from "vue";

export const useMeeting = defineStore('meeting', {
    state: () => ({
        text: "",
        error: null
    }),
    actions: {
    },
})