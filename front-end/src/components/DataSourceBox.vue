<script>
 import axios from 'axios'
 export default {
     props: [ 'source' ],
     data() {
         return {
             html: "",
         }
     },
     methods: {
         get_full_text(id) {
             const vm = this;
             console.log("Getting the full text")
             axios.get('/search/api/full-text/' + id)
                    .then(function(res) {
                        if (res.data && res.data.html) {
                            vm.html = res.data.html;
                        }
                    });
         },
         get_binary_file(id, ext) {
             return '/search/api/download/' + id + ext;
         }
     }
 }
</script>
<template>
  <div>
    <h4 class="font-semibold">
      <span>{{ source.library_name }}</span>
      <span class="px-1" v-if="source.year_edition">({{ source.year_edition }})</span>
    </h4>
    <div v-if="source.description">
      {{ source.description }}
    </div>
    <span v-if="source.uri && source.public">
      <a :href="source.uri" target="_blank">
        <span v-if="source.uri_label">
          {{ source.uri_label }}
        </span>
        <span v-else>
          {{ source.uri }}
        </span>
        <span v-if="source.content_type">
          ({{ source.content_type }})
        </span>
      </a>
    </span>
    <div v-if="source.site_type == 'amusewiki'">
      <div v-if="html">
        <div class="border m-1 p-1 rounded" v-html="html"></div>
      </div>
      <div v-else>
        <button @click="get_full_text(source.data_source_id)">View full text</button>
      </div>
    </div>
    <div v-if="source.shelf_location_code">
      <span>Shelf Location Code:</span> <code>{{ source.shelf_location_code }}</code>
    </div>
    <div v-if="source.downloads">
      <div v-for="dl in source.downloads" :key="dl.code">
        <a :href="get_binary_file(source.data_source_id, dl.ext)">
          {{ dl.desc }}
        </a>
      </div>
    </div>
    <div v-if="source.material_description">
      {{ source.material_description }}
    </div>
    <div>
      <code>ID: {{ source.identifier }}</code>
    </div>
  </div>    
</template>
