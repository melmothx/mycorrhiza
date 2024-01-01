<script>
 import EntryDetails from './EntryDetails.vue'
 import axios from 'axios'
 export default {
     props: [ 'entry_id' ],
     emit: [ 'close', 'changeId' ],
     components: { EntryDetails },
     data() {
         return {
             record: {}
         }
     },
     methods: {
         fetch_record() {
             const vm = this;
             console.log("Fetch " + vm.entry_id);
             axios.get('/search/api/entry/' + vm.entry_id)
                  .then(function(res) {
                      vm.record = res.data
                  });
         }
     },
     mounted () {
         this.fetch_record()
     },
     watch: {
         entry_id(new_id, old_id) {
             console.log("Id changed from " + old_id + " to " + new_id);
             this.fetch_record()
         }
     },
 }
</script>
<template>
  <div class="fixed top-0 left-0 right-0 z-50 bg-white h-full overflow-y-auto">
    <div class="border rounded m-5 p-2 font-serif">
      <div class="flex">
        <div class="flex-grow">
          <EntryDetails :record="record"></EntryDetails>
        </div>
        <div>
          <button class="font-sans border rounded bg-pink-500 hover:bg-pink-700 text-white font-semibold p-1"
                  type="button" @click="$emit('close')">Close</button>
        </div>
      </div>
      <div v-if="record.original_entry"
           @click="$emit('changeId', record.original_entry.id)"
           class="border rounded my-1 p-1 cursor-pointer">
        <EntryDetails :record="record.original_entry">Original title:</EntryDetails>
      </div>
      <div v-if="record.translations && record.translations.length > 0">
        <div v-for="translation in record.translations" :key="translation.id">
          <div @click="$emit('changeId', translation.id)"
            class="border rounded my-1 p-1 cursor-pointer">
            <EntryDetails :record="translation">Translation:</EntryDetails>
          </div>
        </div>
      </div>
      <div class="mb-2 text-sm" v-for="source in record.data_sources" :key="source.identifier">
        <span class="font-semibold">{{ source.site_name }}: </span>
        <span v-if="source.uri">
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
          <button @click="get_full_text(source.data_source_id)">View full text</button>
        </div>
        <div v-if="source.shelf_location_code">
          <span>Shelf Location Code:</span> <code>{{ source.shelf_location_code }}</code>
        </div>
        <div v-if="source.downloads">
          <div v-for="dl in source.downloads" :key="dl.code">
            <button @click="get_binary_file(source.data_source_id, dl.ext)">
              {{ dl.desc }}
            </button>
          </div>
        </div>
        <div v-if="source.material_description">
          {{ source.material_description }}
        </div>
        <div>
          <code>ID: {{ source.identifier }}</code>
        </div>
      </div>
    </div>
  </div>
</template>
