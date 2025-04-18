<script>
 import axios from 'axios'
 import { bookbuilder } from '../stores/bookbuilder.js'
 import ReportErrorPopUp from './ReportErrorPopUp.vue'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     props: [ 'source', 'short' ],
     components: {
         ReportErrorPopUp
     },
     data() {
         return {
             html: "",
             show_html: false,
             show_pdf_reader: false,
             working: false,
             added_to_the_bookbuilder: false,
             bookbuilder,
         }
     },
     mounted() {
         console.log("Restoring the bookbuilder");
         this.bookbuilder.restore();
     },
     methods: {
         toggle_full_text() {
             this.show_pdf_reader = false;
             this.show_html = !this.show_html;
             if (this.show_html && !this.html) {
                 this.working = true;
                 this.get_full_text();
             }
         },
         toggle_pdf_reader() {
             this.show_html = false;
             this.show_pdf_reader = !this.show_pdf_reader;
         },
         get_full_text() {
             const vm = this;
             console.log("Getting the full text")
             axios.get('/collector/api/full-text/' + vm.source.data_source_id)
                    .then(function(res) {
                        vm.working = false;
                        if (res.data && res.data.html) {
                            let html_body = res.data.html;
                            if (html_body.includes('class="table-of-contents"')) {
                                vm.html = html_body;
                            }
                            else {
                                /* fill the grid with a dummy element */
                                vm.html = '<div></div>' + html_body;
                            }
                        }
                    });
         },
         get_binary_file(id, ext) {
             return '/collector/api/download/' + id + ext;
         },
         can_have_full_text() {
             const src = this.source;
             if (src.site_type == 'amusewiki') {
                 if (src.aggregated && src.aggregated.length == 0) {
                     return true;
                 }
             }
             if (src.site_type == 'calibretree') {
                 if (src.downloads && src.downloads.filter((e) => e.ext == '.txt').length) {
                     return true;
                 }
             }
             return false;
         },
         has_pdf_only() {
             if (!this.can_have_full_text()) {
                 const src = this.source;
                 if (src.site_type == 'calibretree') {
                     if (src.downloads && src.downloads.filter((e) => e.ext == '.pdf').length) {
                         return true;
                     }
                 }
             }
             return false;
         },
         pdf_reader() {
             const src = this.source;
             if (src.downloads) {
                 if (src.downloads.find((e) => e.ext == '.pdf')) {
                     return '/pdfjs/web/viewer.html?file=' + this.get_binary_file(src.data_source_id, '.pdf');
                 }
             }
             return false;
         },
         add_to_bookbuilder() {
             let args = {
                 action: "add",
                 add: this.source.data_source_id,
                 session_id: this.bookbuilder.session_id,
             };
             axios.post('/collector/api/bookbuilder', args)
                  .then(res => {
                      console.log(res.data)
                      if (res.data.session_id) {
                          this.bookbuilder.session_id = res.data.session_id;
                          this.added_to_the_bookbuilder = true;
                      }
                  });
             console.log(this.source);
         },
         can_have_the_bookbuilder() {
             const src = this.source;
             if (src.downloads) {
                 if (src.downloads.find((e) => e.ext == '.muse') && src.downloads.find((e) => e.ext == '.zip')) {
                     return true;
                 }
             }
             return false;
         }
     }
 }
</script>
<template>
  <div>
    <div v-if="short"
         class="bg-linear-to-tr from-old-copper-300 to-old-copper-200 px-2 py-2 rounded-t">
      <h3 class="font-semibold"><slot></slot></h3>
    </div>
    <div v-else
         class="bg-linear-to-tr from-old-copper-800 to-old-copper-700 font-semibold rounded-tl-3xl p-2 text-right">
      <h3 class="font-semibold text-white"><slot></slot></h3>
      <h4 class="font-semibold text-white" :id="`library-${source.library_id}`" v-if="!short">
        <router-link :to="{ name: 'library_view', params: { id: source.library_id } }">
          <span class="text-white">{{ source.library_name }}</span>
        </router-link>
      </h4>
    </div>
    <div v-if="source.authors && source.authors.length" class="p-2 bg-perl-bush-50 border-b border-old-copper-100">
      <div v-for="author in source.authors" :key="author">
        {{ author }}
      </div>
    </div>
    <div class="bg-perl-bush-50 p-2">
      <div class="flex">
        <h3 class="font-semibold mr-1 grow" v-if="source.title">
          {{ source.title }}
        </h3>
        <div class="px-2 font-bold" v-if="source.year_edition">
          {{ source.year_edition }}
        </div>
        <div class="font-bold" v-if="source.languages">
          <span class="bg-linear-to-tr from-spectra-700 to-spectra-900 rounded-sm p-1 shadow-md ml-2 text-white"
                v-for="lang in source.languages" :key="lang">
            {{ lang }}
          </span>
        </div>
      </div>
      <h4 class="italic" v-if="source.subtitle">
        {{ source.subtitle }}
      </h4>
      <div class="my-2" v-if="source.description && !short">
        {{ source.description }}
      </div>
      <table class="my-4 w-full">
        <tr class="border-b border-t p-2" v-if="source.shelf_location_code">
          <td class="p-1 pr-2">
            {{ $gettext('Shelf Location Code') }}
          </td>
          <td>
            <code>{{ source.shelf_location_code }}</code>
          </td>
        </tr>
        <tr class="border-b border-t p-2" v-if="source.material_description">
          <td class="p-1 pr-2">
            {{ $gettext('Material Description') }}
          </td>
          <td>
            {{ source.material_description }}
          </td>
        </tr>
        <tr class="border-b border-t p-2" v-if="source.isbn">
          <td class="p-1 pr-2">
            {{ $gettext('ISBN') }}
          </td>
          <td>
            <code>{{ source.isbn }}</code>
          </td>
        </tr>
        <tr class="border-b border-t p-2" v-if="source.publisher">
          <td class="p-1 pr-2">
            {{ $gettext('Publisher') }}
          </td>
          <td>
            {{ source.publisher }}
          </td>
        </tr>
        <tr class="border-b border-t p-2" v-if="source.edition_statement">
          <td class="p-1 pr-2">
            {{ $gettext('Edition') }}
          </td>
          <td>
            {{ source.edition_statement }}
          </td>
        </tr>
        <tr class="border-b border-t p-2"
            v-if="source.place_date_of_publication_distribution && source.place_date_of_publication_distribution != source.year_edition">
          <td class="p-1 pr-2">
            {{ $gettext('Edition Place and Date') }}
          </td>
          <td>
            {{ source.place_date_of_publication_distribution }}
          </td>
        </tr>
        <tr class="border-b border-t p-2" v-if="source.site_type == 'generic' && source.uri && source.uri_label">
          <td class="p-1 pr-2">
            {{ source.uri_label }}
          </td>
          <td>
            <a :href="source.uri">{{ source.uri }}</a>
          </td>
        </tr>
        <tr class="border-b border-t p-2" v-if="source.koha_url">
          <td class="p-1 pr-2">
            {{ $gettext('OPAC page') }}
          </td>
          <td>
            <a :href="source.koha_url">{{ source.koha_url }}</a>
          </td>
        </tr>
      </table>
      <div v-if="has_pdf_only()">
        <div class="flex flex-wrap" v-if="source.downloads && source.downloads.length">
          <div v-for="dl in source.downloads" :key="dl.code" class="btn-primary m-1 p-1 rounded-sm">
            <a :href="get_binary_file(source.data_source_id, dl.ext)">
              {{ dl.desc }}
            </a>
          </div>
        </div>
      </div>
      <div class="flex mb-8">
        <div class="grow"></div>
        <div v-if="can_have_full_text()">
          <button class="btn-accent m-1 px-4 py-1 rounded-sm shadow-lg" @click="toggle_full_text">{{ $gettext('Full text') }}</button>
        </div>
        <div v-if="pdf_reader()">
          <button class="btn-accent m-1 px-4 py-1 rounded-sm shadow-lg" @click="toggle_pdf_reader">{{ $gettext('View PDF') }}</button>
        </div>
        <div v-if="can_have_the_bookbuilder() && !added_to_the_bookbuilder">
          <button class="btn-accent m-1 px-4 py-1 rounded-sm shadow-lg" @click="add_to_bookbuilder">
            {{ $gettext('Add to the Book Builder') }}
          </button>
        </div>
        <router-link v-if="added_to_the_bookbuilder" :to="{ name: 'bookbuilder' }" class="bg-linear-to-tr from-spectra-700 to-spectra-900 m-1 px-4 py-1 rounded-sm shadow-lg text-white font-bold">
          {{ $gettext('Added to the Book Builder!') }}
        </router-link>
        <div v-if="source.report_error">
          <ReportErrorPopUp :data_source_id="source.data_source_id"
                            :data_source_title="source.title"
                            :library_name="source.library_name" />
        </div>
        <div class="grow"></div>
      </div>
      <div v-if="show_html">
        <!-- mettere sotto full text -->
        <div class="flex flex-wrap" v-if="source.downloads && source.downloads.length">
          <div v-for="dl in source.downloads" :key="dl.code" class="btn-primary m-1 p-1 rounded-sm">
            <a :href="get_binary_file(source.data_source_id, dl.ext)">
              {{ dl.desc }}
            </a>
          </div>
          <div class="btn-primary m-1 p-1 rounded-sm" v-if="source.uri && source.public">
            <a :href="source.uri" target="_blank">
              <span class="text-white" v-if="source.uri_label">
                {{ source.uri_label }}
              </span>
              <span class="text-white" v-else-if="source.content_type && source.content_type === 'text/html'">
                {{ $gettext('Landing page') }}
              </span>
              <span class="text-white" v-else>
                ({{ source.content_type }})
              </span>
            </a>
          </div>
        </div>
        <div class="text-base border m-1 p-3 rounded-sm bg-linear-to-t from-perl-bush-100 to-perl-bush-200">
          <div v-if="working" class="m-2 text-center">
            <span class="animate-ping text-claret-900">{{ $gettext('Working') }}</span>
          </div>
          <div class="full-text-container grid gap-4 grid-cols-[15em_1fr]"
               v-html="html"></div>
        </div>
      </div>
      <div class="my-4 p-1 shadow-sm" v-if="show_pdf_reader && pdf_reader()">
        <iframe :src="pdf_reader()" width="100%" height="500px"></iframe>
      </div>
      <div class="mt-4 mx-auto text-[10px] text-perl-bush-400" v-if="source.identifier">
        <code>{{ source.identifier }}</code>
      </div>
    </div>
  </div>
</template>
