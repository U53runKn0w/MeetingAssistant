import {defineStore} from 'pinia'
import {dummyMeeting} from "@/js/etc.js";

export const useChat = defineStore('chat', {
    state: () => ({
        messages: [],
        question: '',
        meeting: dummyMeeting,
        buttonsShow: false
    }),
    actions: {
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