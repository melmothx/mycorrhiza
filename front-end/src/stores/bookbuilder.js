import { reactive } from 'vue'

export const bookbuilder = reactive({
    session_id: null,
    set_session_id(session_id) {
        this.session_id = session_id;
    },
    reset_session_id() {
        this.session_id = null;
    }
})
