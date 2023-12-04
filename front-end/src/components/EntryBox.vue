<script>
 export default {
     props: ['record'],
     data() {
         return {
             show_details: false,
         }
     },
     computed: {
         title() {
             return this.record.title[0]['value'];
         },
         subtitle() {
             return this.record.title[1]['value'];
         },
         date() {
             if (this.record.date) {
                 return this.record.date[0]['value'];
             }
         },
     },
     methods: {
         drag_element(e, merge_type, id, label) {
             if (e) {
                 console.log("Dragging entry: " + [merge_type, id, label].join(' '))
                 e.dataTransfer.dropEffect = 'copy';
                 e.dataTransfer.effectAllowed = 'copy';
                 e.dataTransfer.setData('ID', id);
                 e.dataTransfer.setData('Label', label);
                 e.dataTransfer.setData('Merge', merge_type);
             }
         },
         toggle_show_details() {
             this.show_details = this.show_details ? false : true;
         },
     },
 }
</script>
<template>
  <div class="border p-2 border-gray-200 rounded mt-2 font-serif">
    <div class="p-1">
      <div v-if="record.creator">
        <div v-for="author in record.creator" :key="author.id">
          <div class="drag-el cursor-grab active:cursor-grabbing drag-author bg-gray-100 px-3 py-1 rounded"
               draggable="true" @dragstart="drag_element($event, 'author', author.id, author.value)">
            {{ author.value }}
          </div>
        </div>
      </div>
      <div class="drag-el drag-title cursor-grab active:cursor-grabbing p-2"
           draggable="true" @dragstart="drag_element($event, 'entry', record.entry_id, title)"
           @click="toggle_show_details">
        <h2 class="font-semibold">{{ title }}
          <small v-if="date">
            ({{ date }})
          </small>
        </h2>
        <h3 class="italic" v-if="subtitle">{{ subtitle }}</h3>
      </div>
      <div v-if="show_details" class="p-2">
        <div v-for="desc in record.description" :key="desc.id" class="text-sm mb-3 pb-3 border-b">
          <p>
            {{ desc.value }}
          </p>
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
      </div>
    </div>
  </div>
</template>
<style scoped>
</style>
