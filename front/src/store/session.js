import {defineStore} from "pinia";

export const useSession = defineStore('session', {
    state: () => ({
        sessionId: '',
        history: []
    }),
    actions: {},
})