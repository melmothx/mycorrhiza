<script>
 import axios from 'axios'
 export default {
     props: [ 'source', 'short' ],
     data() {
         return {
             html: "",
             show_html: false,
             working: false,
         }
     },
     methods: {
         toggle_full_text() {
             this.show_html = !this.show_html;
             if (this.show_html && !this.html) {
                 this.working = true;
                 this.get_full_text();
             }
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
                     return 1;
                 }
             }
             return 0;
         }
     }
 }
</script>
<template>
  <div>
    <div v-if="short"
         class="bg-gradient-to-tr from-old-copper-300 to-old-copper-200 px-2 py-2 rounded-t">
      <h3 class="font-semibold"><slot></slot></h3>
    </div>
    <div v-else
         class="bg-gradient-to-tr from-old-copper-800 to-old-copper-700 font-semibold rounded-tl-3xl p-2">
      <h3 class="font-semibold text-white"><slot></slot></h3>
      <h4 class="font-semibold text-white" v-if="!short">
        <span class="text-white">{{ source.library_name }}</span>
        <span class="text-white px-1" v-if="source.year_edition">({{ source.year_edition }})</span>
      </h4>
    </div>
    <div v-if="source.authors && source.authors.length" class="p-2 bg-gradient-to-t from-vanilla-ice-200 to-vanilla-ice-300 text-claret-900">
      <div v-for="author in source.authors" :key="author">
        {{ author }}
      </div>
    </div>
    <div class="bg-perl-bush-50 p-2">
      <div class="flex">
        <h3 class="font-semibold mr-1 flex-grow" v-if="source.title">
          {{ source.title }}
        </h3>
        <div v-if="source.languages">
          <div v-for="lang in source.languages" :key="lang">
            [{{ lang }}]
          </div>
        </div>
      </div>
      <h4 class="italic" v-if="source.subtitle">
        {{ source.subtitle }}
      </h4>
      <div class="my-2" v-if="source.description && !short">
        {{ source.description }}
      </div>
      <div v-if="source.shelf_location_code">
        <span>{{ $gettext('Shelf Location Code') }}</span> <code>{{ source.shelf_location_code }}</code>
      </div>
      <div v-if="source.material_description">
        {{ source.material_description }}
      </div>
      <div>
        <code>{{ $gettext('ID:') }}</code> <code>{{ source.identifier }}</code>
      </div>
      <div class="flex flex-wrap" v-if="source.downloads && source.downloads.length">
        <div v-for="dl in source.downloads" :key="dl.code" class="btn-primary m-1 p-1 rounded">
          <a :href="get_binary_file(source.data_source_id, dl.ext)">
            {{ dl.desc }}
          </a>
        </div>
        <div class="btn-primary m-1 p-1 rounded" v-if="source.uri && source.public">
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
        <div v-if="can_have_full_text()">
          <button class="btn-accent m-1 p-1 rounded" @click="toggle_full_text">{{ $gettext('Full text') }}</button>
        </div>
      </div>
      <div v-if="show_html">
        <div class="text-base border m-1 p-3 rounded bg-gradient-to-t from-perl-bush-100 to-perl-bush-200">
          <div v-if="working" class="m-2 text-center">
            <span class="animate-ping text-claret-900">{{ $gettext('Working') }}</span>
          </div>
          <div class="full-text-container grid gap-4 grid-cols-[15em_1fr]"
               v-html="html"></div>
        </div>
      </div>
    </div>
  </div>
</template>
