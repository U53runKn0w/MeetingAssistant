import {defineStore} from "pinia";
import {dummyMeeting} from "@/js/etc.js";

export const useMeeting = defineStore('meeting', {
    state: () => ({
        text: dummyMeeting,
        error: null
    }),
    actions: {
    },
})