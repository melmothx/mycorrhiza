<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import {
     PencilSquareIcon,
     HandRaisedIcon,
 } from '@heroicons/vue/24/solid'
 export default {
     props: [ "agent", "can_edit" ],
     data() {
         return {
             error: null,
             edited: false,
             show_editing: false,
             agent_editable_data: {},
         }
     },
     components: {
         PencilSquareIcon,
         HandRaisedIcon,
     },
     methods: {
         edit_agent() {
             console.log("Editing");
             if (this.show_editing) {
                 this.show_editing = false;
             }
             else {
                 axios.get('/collector/api/agents/' + this.agent.id)
                      .then((res) => {
                          this.error = res.data.error;
                          this.agent_editable_data = res.data.agent;
                          if (res.data.agent) {
                              this.edited = true;
                              this.show_editing = true;
                          }
                      })
                      .catch(error => {
                          this.error = error;
                      });
             }
         },
         update_agent() {
             console.log("Updating");
             axios.post('/collector/api/agents/' + this.agent.id,
                        this.agent_editable_data)
                  .then((res) => {
                      this.error = res.data.error;
                      this.agent_editable_data = res.data.agent;
                      if (res.data.agent) {
                          this.show_editing = false;
                      }
                  })
                  .catch(error => {
                      this.error = error;
                  });
         },
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
    <div v-if="edited && !show_editing">
      <div v-if="agent_editable_data.first_name">
        {{ $gettext('First Name: %1', agent_editable_data.first_name) }}
      </div>
      <div v-if="agent_editable_data.last_name">
        {{ $gettext('Last Name: %1', agent_editable_data.last_name) }}
      </div>
      <div v-if="agent_editable_data.description" class="my-2" >
        {{ agent_editable_data.description }}
      </div>
      <div v-if="agent_editable_data.viaf_identifier">
        {{ $gettext('VIAF: %1', agent_editable_data.viaf_identifier) }}
      </div>
      <div v-if="agent_editable_data.canonical" class="font-bold text-gray-500">
        {{ $gettext('See “%1”', agent_editable_data.canonical.name) }}
      </div>
    </div>
    <div v-else>
      <div v-if="agent.first_name">
        {{ $gettext('First Name: %1', agent.first_name) }}
      </div>
      <div v-if="agent.last_name">
        {{ $gettext('Last Name: %1', agent.last_name) }}
      </div>
      <div v-if="agent.description" class="my-2" >
        {{ agent.description }}
      </div>
      <div v-if="agent.viaf_identifier">
        {{ $gettext('VIAF: %1', agent.viaf_identifier) }}
      </div>
      <div v-if="agent.canonical" class="font-bold text-gray-500">
        {{ $gettext('See “%1”', agent.canonical.name) }}
      </div>
    </div>
    <div class="flex" v-if="!agent.canonical && can_edit">
      <span @click="edit_agent" class="text-spectra-600
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
    <div v-if="show_editing">
      <form @submit.prevent="update_agent">
        <div>
          <label class="mcrz-label" :for="`agent-first-name-${agent.id}`">{{ $gettext('First Name') }}</label>
          <div class="flex">
            <input :id="`agent-first-name-${agent.id}`" class="mcrz-input" v-model="agent_editable_data.first_name" />
          </div>
        </div>
        <div>
          <label class="mcrz-label" :for="`agent-last-name-${agent.id}`">{{ $gettext('Last Name') }}</label>
          <div class="flex">
            <input :id="`agent-last-name-${agent.id}`" class="mcrz-input" v-model="agent_editable_data.last_name" />
          </div>
        </div>
        <div>
          <label class="mcrz-label" :for="`agent-description-${agent.id}`">{{ $gettext('Description') }}</label>
          <div class="flex">
            <textarea class="mcrz-input" v-model="agent_editable_data.description"
                      :id="`agent-description-${agent.id}`"></textarea>
          </div>
        </div>
        <div>
          <label class="mcrz-label" :for="`agent-first-name-${agent.id}`">{{ $gettext('VIAF Identifier') }}</label>
          <div class="flex">
            <input type="number"
                   step="1"
                   class="mcrz-input" v-model="agent_editable_data.viaf_identifier"
                   :id="`agent-first-name-${agent.id}`" />
          </div>
        </div>
        <button class="btn-primary my-2 p-1" type="submit">
          {{ $gettext('Submit') }}
        </button>
      </form>
    </div>
  </div>
</template>
