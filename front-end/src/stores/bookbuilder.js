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
            parindent: 15,
            linespacing: 1,
            tex_tolerance: 200,
            tex_emergencystretch: 30,
            headings: '0',
            signature_2up: '0',
            signature_4up: '0',
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
        return this.collection_data.sansfontsections;
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
    needs_signature_2up() {
        const imposition_schema = this.collection_data.imposition_schema;
        const schemas = [ '2up', 'duplex2up', '2down' ];
        return schemas.includes(imposition_schema);
    },
    needs_signature_4up() {
        const imposition_schema = this.collection_data.imposition_schema;
        const schemas = [ '4up' ];
        return schemas.includes(imposition_schema);
    },
    api_collection_data() {
        const bbargs = { ...this.collection_data };
        // possible interpolation here
        if (!bbargs.papersize && bbargs.papersize_width && bbargs.papersize_height) {
            bbargs.papersize = `${bbargs.papersize_width}mm:${bbargs.papersize_height}mm`;
        }
        bbargs.bcor = (bbargs.binding_correction || 0) + 'mm';
        let has_custom_dimensions = false;
        if (!bbargs.division_factor || bbargs.division_factor == 0) {
            // just set the default
            bbargs.division = 9;
            has_custom_dimensions = true;
        }
        else {
            bbargs.division = bbargs.division_factor;
        }
        for (const field of ['areaset_width', 'areaset_height', 'geometry_top_margin', 'geometry_outer_margin']) {
            if (has_custom_dimensions) {
                if (bbargs[field]) {
                    bbargs[field] = `${bbargs[field]}mm`;
                }
            }
            else {
                delete bbargs[field];
            }
        }
        // add the pt measures
        for (const ptfield of ['tex_emergencystretch']) {
            if (bbargs[ptfield]) {
                bbargs[ptfield] = `${bbargs[ptfield]}pt`;
            }
            else {
                delete bbargs[ptfield];
            }
        }
        for (const boolfield of ['twoside',
                                 'notoc',
                                 'nofinalpage',
                                 'nocoverpage',
                                 'body_only',
                                 'impressum',
                                 'sansfontsections',
                                 'nobold',
                                 'start_with_empty_page',
                                 'ignore_cover',
                                 'continuefootnotes',
                                 'centerchapter',
                                 'centersection',
                                ]) {
            if (bbargs[boolfield]) {
                bbargs[boolfield] = 1;
            }
            else {
                delete bbargs[boolfield];
            }
        }
        if (bbargs.linespacing <= 1) {
            delete bbargs.linespacing;
        }
        return bbargs;
    },

})
