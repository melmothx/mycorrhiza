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
             return this.record.title[0];
         },
         subtitle() {
             return this.record.title[1];
         },
         authors() {
             if (this.record.creator) {
                 return this.record.creator.join(' ');
             }
             else {
                 return '';
             }
         },
     },
     methods: {
         drag_title(e) {
             if (e) {
                 console.log("Dragging work: " + this.record.work_id);
                 e.dataTransfer.dropEffect = 'copy';
                 e.dataTransfer.effectAllowed = 'copy';
                 e.dataTransfer.setData('Work', this.record.work_id);
                 e.dataTransfer.setData('WorkTitle', this.title);
             }
         },
         drag_author(e, author) {
             if (e) {
                 console.log("Dragging author: " + author);
                 e.dataTransfer.dropEffect = 'copy';
                 e.dataTransfer.effectAllowed = 'copy';
                 e.dataTransfer.setData('Author', author);
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
        <div v-for="author in record.creator">
          <div class="drag-el cursor-grab active:cursor-grabbing drag-author bg-gray-100 px-3 py-1 rounded"
               draggable="true" @dragstart="drag_author($event, author)">
            {{ author }}
          </div>
        </div>
      </div>
      <div class="drag-el drag-title cursor-grab active:cursor-grabbing p-2"
           draggable="true" @dragstart="drag_title($event)" @click="toggle_show_details">
        <h2 class="font-semibold">{{ title }}</h2>
        <h3 class="italic" v-if="subtitle">{{ subtitle }}</h3>
      </div>
      <div v-if="show_details" class="p-2">
        <div class="text-sm mb-3 pb-3 border-b" v-if="record.description">
          <template v-for="desc in record.description">
            <p v-if="desc.length > 1">
              {{ desc }}
            </p>
          </template>
        </div>
        <div class="mb-2" v-for="source in record.data_sources" :key="source.identifier">
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
          <span v-else-if="source.shelf_location_code">
            <code>{{ source.shelf_location_code }}</code>
          </span>
          <span v-else>
            <code>{{ source.identifier }}</code>
          </span>
          <div v-if="source.material_description">
            {{ source.material_description }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
</style>
