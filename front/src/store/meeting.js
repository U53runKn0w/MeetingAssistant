import {defineStore} from "pinia";

export const useMeeting = defineStore('meeting', {
    state: () => ({
        text: "",
        error: null
    }),
    actions: {
    },
})