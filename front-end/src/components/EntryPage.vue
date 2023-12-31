<script>
 import axios from 'axios'
 export default {
     props: [ 'entry_id' ],
     emit: [ 'close' ],
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
  <div class="flex">
    <div class="flex-grow">
      <h1>{{ record.title }}</h1>
      <h2>{{ record.subtitle }}</h2>
      <div>
        {{ record.body }}
      </div>
    </div>
    <div>
      <button type="button" @click="$emit('close')">Close</button>
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
    <div if="source.shelf_location_code">
      <span>Shelf Location Code:</span> <code>{{ source.shelf_location_code }}</code>
    </div>
    <div v-if="source.material_description">
      {{ source.material_description }}
    </div>
    <div>
      <code>ID: {{ source.identifier }}</code>
    </div>
  </div>

</template>
