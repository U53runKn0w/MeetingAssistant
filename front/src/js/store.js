// stores/counter.js
import {defineStore} from 'pinia'

export const useConversation = defineStore('conversation', {
    state: () => ({
        messages: [],
        question: ''
    }),
    actions: {
        extractObservation(){
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