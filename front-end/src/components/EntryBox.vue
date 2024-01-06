<script>
 import ExclusionButton from './ExclusionButton.vue'
 export default {
     components: { ExclusionButton },
     props: [ 'record', 'can_set_exclusions', 'can_merge' ],
     emits: [ 'refetchResults', 'selectEntry' ],
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
             else {
                 return "";
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
     },
 }
</script>
<template>
  <div class="border p-2 border-gray-200 rounded mt-2 font-serif">
    <div class="p-1">
      <div v-if="record.creator">
        <div v-for="author in record.creator" :key="author.id" class="flex">
          <div class="flex-grow bg-gray-100 px-3 py-1 rounded">
            {{ author.value }}
          </div>
          <div v-if="can_merge">
            <span class="drag-el cursor-grab active:cursor-grabbing drag-author
                         border-2 rounded-full text-sm px-2 bg-pink-800 text-white font-semibold"
                  draggable="true" @dragstart="drag_element($event, 'author', author.id, author.value)">
              Merge
            </span>
          </div>
          <div v-if="can_set_exclusions">
            <ExclusionButton :object_id="author.id"
                             object_type="author"
                             @refetch-results="$emit('refetchResults')" />
          </div>
        </div>
      </div>
      <div>
        <div class="font-semibold flex">
          <h2 class="flex-grow cursor-pointer" @click="$router.push({name: 'entry', params: { id: record.entry_id } })">
            {{ title }}
            <small v-if="date">
              ({{ date }})
            </small>
          </h2>
          <div v-if="can_merge">
            <span class="drag-el drag-title cursor-grab active:cursor-grabbing border-2 rounded-full text-sm px-2 bg-pink-800 text-white font-semibold"
              draggable="true" @dragstart="drag_element($event, 'entry', record.entry_id, title)">
              Merge
            </span>
          </div>
          <div v-if="can_set_exclusions">
            <ExclusionButton :object_id="record.entry_id"
                             object_type="entry"
                             @refetch-results="$emit('refetchResults')" />
          </div>
        </div>
        <h3 class="italic" v-if="subtitle">{{ subtitle }}</h3>
        <div v-for="desc in record.description" :key="desc.id" class="text-sm pb-3 mt-2">
          <p>
            {{ desc.value }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
</style>
