import { reactive } from 'vue'

export const bookbuilder = reactive({
    session_id: null,
    job_id: null,
    text_list: [],
    job_produced: null,
    error: null,
    status: null,
    loaded: false,
    collection_data: null,
    default_collection_data() {
        return {
            papersize: "a4",
            mainfont: "DejaVu Serif",
            sansfont: "DejaVu Sans",
            monofont: "DejaVu Sans Mono",
            imposition_schema: "",
            fontsize: "12",
            division_factor: "12",
            binding_correction: "0",
            opening: 'any',
        };
    },
    save() {
        console.log("Saving the state");
        localStorage.setItem('bookbuilder', JSON.stringify({
            session_id:   this.session_id,
            job_id:       this.job_id,
            text_list:    this.text_list,
            job_produced: this.job_produced,
            error:        this.error,
            status:       this.status,
            collection_data: this.collection_data || this.default_collection_data(),
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
                this.collection_data =  stored_obj.collection_data || this.default_collection_data(),
                this.loaded = true;
            }
        }
    },
    reset() {
        this.session_id = null,
        this.job_id = null,
        this.text_list = [],
        this.job_produced = null,
        this.error = null,
        this.status = null,
        this.loaded = true,
        this.collection_data = this.default_collection_data(),
        this.save();
    },
    can_be_compiled() {
        if (this.text_list.length > 0 && !this.job_id) {
            return true;
        }
        else {
            return false;
        }
    },
    needs_sans_font() {
        return false;
    },
    needs_virtual_header() {
        if (this.text_list.length > 1) {
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
    needs_areaset_height() {
        if (this.collection_data.division_factor == 0 && !this.collection_data.areaset_height) {
            return true;
        }
        else {
            return false;
        }
    },
    needs_areaset_width() {
        if (this.collection_data.division_factor == 0 && !this.collection_data.areaset_width) {
            return true;
        }
        else {
            return false;
        }
    },
    needs_geometry_top_margin() {
        if (!this.collection_data.geometry_top_margin && this.collection_data.geometry_outer_margin) {
            return true;
        }
        else {
            return false;
        }
    },
    needs_geometry_outer_margin() {
        if (!this.collection_data.geometry_outer_margin && this.collection_data.geometry_top_margin) {
            return true;
        }
        else {
            return false;
        }
    },
    api_collection_data() {
        const bbargs = { ...this.collection_data };
        // possible interpolation here
        if (!bbargs.papersize && bbargs.papersize_width && bbargs.papersize_height) {
            bbargs.papersize = `${bbargs.papersize_width}mm:${bbargs.papersize_height}mm`
        }
        bbargs.bcor = (bbargs.binding_correction || 0) + 'mm';
        if (!bbargs.division_factor || bbargs.division_factor == 0) {
            bbargs.division = 9;
        }
        else {
            bbargs.division = bbargs.division_factor;
        }
        for (const field of ['areaset_width', 'areaset_height', 'geometry_top_margin', 'geometry_outer_margin']) {
            if (bbargs[field]) {
                bbargs[field] = `${bbargs[field]}mm`;
            }
        }
        if (bbargs.twoside) {
            bbargs.twoside = 1;
        }
        else {
            bbargs.twoside = 0;
        }
        return bbargs;
    },

})
