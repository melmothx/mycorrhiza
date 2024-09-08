<script>
 import ExclusionButton from './ExclusionButton.vue'
 import { HandRaisedIcon } from '@heroicons/vue/24/solid'
 import LibraryBadges from './LibraryBadges.vue'
 export default {
     components: {
         ExclusionButton, HandRaisedIcon,
         LibraryBadges,
     },
     props: [ 'record', 'can_set_exclusions', 'can_merge' ],
     emits: [ 'refetchResults' ],
     computed: {
         title() {
             return this.record.title[0]['value'];
         },
         subtitle() {
             return this.record.title[1]['value'];
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
  <div class="mb-6 font-serif bg-perl-bush-50 shadow-md">
    <div>
      <div v-if="record.creator"
           class="py-1 bg-gradient-to-t from-vanilla-ice-200 to-vanilla-ice-300 text-claret-900">
        <div v-for="author in record.creator" :key="author.id" class="flex">
          <div class="flex-grow px-3">
            {{ author.value }}
          </div>
          <div v-if="can_merge">
            <span class="drag-el cursor-grab active:cursor-grabbing drag-author
                         text-spectra-600 hover:text-spectra-800 hover:text-spectra-800
                         focus:text-spectra-800"
                  :title="$gettext('Merge')"
                  draggable="true" @dragstart="drag_element($event, 'author', author.id, author.value)">
              <HandRaisedIcon class="h-4 w-4 m-1" />
            </span>
          </div>
          <div v-if="can_set_exclusions">
            <ExclusionButton :object_id="author.id"
                             object_type="author"
                             @refetch-results="$emit('refetchResults')">
              {{ $gettext('Omit author') }}
            </ExclusionButton>
          </div>
        </div>
      </div>
      <div>
        <div class="flex py-2">
          <h2 class="font-semibold flex-grow cursor-pointer px-3"
              @click="$router.push({name: 'entry', params: { id: record.entry_id } })">
            {{ title }}
          </h2>
          <div v-if="record.language" class="px-2">
            <small class="px-2" v-for="l in record.language" :key="l.id">
              [{{ l.value }}]
            </small>
          </div>
          <div v-if="can_merge">
            <span class="drag-el drag-title cursor-grab active:cursor-grabbing
                         text-spectra-600 hover:text-spectra-800 hover:text-spectra-800
                         focus:text-spectra-800"
                  :title="$gettext('Merge')"
                  draggable="true" @dragstart="drag_element($event, 'entry', record.entry_id, title)">
              <HandRaisedIcon class="h-4 w-4 m-1" />
            </span>
          </div>
          <div v-if="can_set_exclusions">
            <ExclusionButton :object_id="record.entry_id"
                             object_type="entry"
                             @refetch-results="$emit('refetchResults')">
              {{ $gettext('Omit single entry') }}
            </ExclusionButton>
          </div>
        </div>
        <h3 class="italic px-3 pb-2" v-if="subtitle">{{ subtitle }}</h3>
        <div class="pb-2">
          <LibraryBadges :data_sources="record.data_sources">
          </LibraryBadges>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
</style>
