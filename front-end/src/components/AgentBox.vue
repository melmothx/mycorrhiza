<script>
 import {
     PencilSquareIcon,
     HandRaisedIcon,
 } from '@heroicons/vue/24/solid'
 export default {
     props: [ "agent", "can_edit" ],
     components: {
         PencilSquareIcon,
         HandRaisedIcon,
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
  <div v-if="agent" class="border border-perl-bush-200 bg-perl-bush-50 p-1 shadow">
    <a :href="`/library/author/${agent.search_link_id}`" target="_blank">
      <h2 class="font-bold">{{ agent.name }}</h2>
    </a>
    <div v-if="agent.first_name">
      {{ $gettext('First Name: %1', agent.first_name) }}
    </div>
    <div v-if="agent.last_name">
      {{ $gettext('Last Name: %1', agent.last_name) }}
    </div>
    <div v-if="agent.description" class="my-2" >
      {{ agent.description }}
    </div>
    <div v-if="agent.canonical" class="font-bold text-gray-500">
      {{ $gettext('See “%1”', agent.canonical.name) }}
    </div>
    <div class="flex" v-if="!agent.canonical && can_edit">
      <span class="text-spectra-600
                   hover:text-spectra-800
                   focus:text-spectra-800">
        <PencilSquareIcon class="w-4 h-4 my-1 mr-2" />
      </span>
      <span class="drag-el cursor-grab active:cursor-grabbing drag-author
                   text-spectra-600
                   hover:text-spectra-800
                   focus:text-spectra-800"
            :title="$gettext('Merge')"
            draggable="true" @dragstart="drag_element($event, 'author', agent.id, agent.name)">
        <HandRaisedIcon class="h-4 w-4 my-1" />
      </span>
    </div>
  </div>
</template>
