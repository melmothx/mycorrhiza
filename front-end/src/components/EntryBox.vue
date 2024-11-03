<script>
 import ExclusionButton from './ExclusionButton.vue'
 import {
     HandRaisedIcon,
     MagnifyingGlassIcon,
 } from '@heroicons/vue/24/solid'
 import LibraryBadges from './LibraryBadges.vue'
 export default {
     components: {
         ExclusionButton, HandRaisedIcon,
         LibraryBadges,
         MagnifyingGlassIcon,
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
         is_translated() {
             if (this.record.translate && this.record.translate.filter((e) => e.id == 'translated').length) {
                 return true;
             }
             else {
                 return false;
             }
         },
         is_translation() {
             if (this.record.translate && this.record.translate.filter((e) => e.id == 'translation').length) {
                 return true;
             }
             else {
                 return false;
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
  <div class="mb-6 font-serif bg-perl-bush-50 shadow-md rounded-tl-2xl">
    <div>
      <div v-if="record.creator"
           class="py-1">
        <div v-for="author in record.creator" :key="author.id" class="flex flex-wrap border-b border-old-copper-100">
          <div class="flex-grow px-3">
            {{ author.value }}
          </div>
          <div>
            <a :title="$gettext('See all entries')"
               target="_blank"
               :href="`/library/author/${author.id}`">
              <MagnifyingGlassIcon class="h-4 w-4 m-1" />
            </a>
          </div>
          <div v-if="can_merge">
            <span class="drag-el cursor-grab active:cursor-grabbing drag-author
                         text-spectra-600
                         hover:text-spectra-800
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
          <router-link class="font-semibold flex-grow cursor-pointer px-3"
                       :to="{name: 'entry', params: { id: record.entry_id } }">
            {{ title }}
          </router-link>
          <div v-if="record.language">
            <router-link :to="{name: 'entry', params: { id: record.entry_id } }">
              <small class="px-2" v-for="l in record.language" :key="l.id">
                <span v-if="is_translation"
                      class="btn-primary p-1 rounded shadow-md"
                      :title="$gettext('This text is a translation')">
                  {{ l.value }}
                </span>
                <span v-else-if="is_translated"
                      :title="$gettext('This text is translated')"
                      class="btn-accent p-1 rounded shadow-md">
                  {{ l.value }}
                </span>
                <span v-else>
                  [{{ l.value }}]
                </span>
              </small>
            </router-link>
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
          <LibraryBadges :data_sources="record.data_sources" :entry_id="record.entry_id">
          </LibraryBadges>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
</style>
