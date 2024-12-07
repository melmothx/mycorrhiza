import { reactive } from 'vue'

export const bookbuilder = reactive({
    session_id: null,
    job_id: null,
    text_list: [],
    job_produced: null,
    error: null,
    status: null,
    loaded: false,
    save() {
        console.log("Saving the state");
        localStorage.setItem('bookbuilder', JSON.stringify({
            session_id:   this.session_id,
            job_id:       this.job_id,
            text_list:    this.text_list,
            job_produced: this.job_produced,
            error:        this.error,
            status:       this.status,
        }));
    },
    restore() {
        if (!this.loaded) {
            const stored = localStorage.getItem('bookbuilder');
            if (stored) {
                const stored_obj = JSON.parse(stored);
                console.log("Loading bookbuilder session");
                this.session_id   = stored_obj.session_id;
                this.job_id       = stored_obj.job_id;
                this.text_list    = stored_obj.text_list;
                this.job_produced = stored_obj.job_produced;
                this.error        = stored_obj.error;
                this.status       = stored_obj.status;
                this.loaded = true;
            }
        }
    },
    can_be_compiled() {
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
            this.save();
        }
    },
    finish() {
        this.job_produced = this.job_id;
        this.job_id = null;
        this.save();
    },
    fail(error) {
        this.job_id = null;
        this.error = error;
        this.save();
    },
})
