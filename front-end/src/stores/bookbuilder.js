import { reactive } from 'vue'

export const bookbuilder = reactive({
    session_id: null,
    job_id: null,
    text_list: [],
    job_produced: null,
    error: null,
    status: null,
    can_be_compiled() {
        console.log("Called can be compiled");
        if (this.text_list.length > 0 && !this.job_id && !this.job_produced) {
            return true;
        }
        else {
            return false;
        }
    },
    add_text(data) {
        if (data.texts && data.session_id) {
            this.session_id = data.session_id;
            this.text_list = data.texts;
            this.job_produced = null;
            this.status = null;
        }
    },
    finish() {
        this.job_produced = this.job_id;
        this.job_id = null;
    },
    fail(error) {
        this.job_id = null;
        this.error = error;
    },
})
