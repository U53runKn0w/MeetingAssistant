import {defineStore} from 'pinia';

export const useErrorStore = defineStore('error', {
    state: () => ({
        message: '',
        show: false
    }),
    actions: {
        setError(msg) {
            this.message = msg;
            this.show = true;
            // setTimeout(() => {
            //     this.show = false;
            // }, 3000)
        },
        clearError() {
            this.show = false;
            this.message = '';
        }
    }
});