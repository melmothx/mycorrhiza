<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import {
     PencilSquareIcon,
     HandRaisedIcon,
 } from '@heroicons/vue/24/solid'
 export default {
     props: [ "agent", "can_edit", "short" ],
     data() {
         return {
             error: null,
             edited: false,
             show_editing: false,
             agent_editable_data: {},
             display_details: {},
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
                          this.display_details = { ...this.agent_editable_data };
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
     mounted() {
         this.display_details = { ...this.agent };
     },
     computed: {
         full_name() {
             const details = this.display_details;
             const full_name_pieces = [ details.first_name, details.middle_name, details.last_name ];
             const full_name = full_name_pieces.filter((w) => w).join(" ");
             if (full_name != this.agent.name) {
                 return full_name;
             }
             else {
                 return "";
             }
         }
     },
 }
</script>
<template>
  <div v-if="agent" class="border border-perl-bush-200 bg-perl-bush-50 p-4 shadow-sm rounded-sm">
    <div v-if="short">
      <h2 class="font-bold">{{ agent.name }}</h2>
    </div>
    <div v-else>
      <a :href="`/library/author/${agent.search_link_id}`" target="_blank">
        <h2 class="font-bold">{{ agent.name }}</h2>
      </a>
    </div>
    <div v-if="full_name">
      <span class="pr-1" v-if="display_details.first_name">
        {{ display_details.first_name }}
      </span>
      <span class="pr-1" v-if="display_details.middle_name">
        {{ display_details.middle_name }}
      </span>
      <span class="pr-1" v-if="display_details.last_name">
        {{ display_details.last_name }}
      </span>
    </div>
    <div v-if="display_details.date_of_birth || display_details.date_of_death">
      (<span v-if="display_details.date_of_birth">
      <span v-if="display_details.place_of_birth">{{ display_details.place_of_birth }}&nbsp;</span>
      <span>{{ display_details.date_of_birth }}</span>
      </span>
      <span>&nbsp;—&nbsp;</span>
     <span v-if="display_details.date_of_death">
      <span v-if="display_details.place_of_death">{{ display_details.place_of_death }}&nbsp;</span>
      <span>{{ display_details.date_of_death }}</span>
      </span>)
    </div>
    <div v-if="display_details.viaf_identifier">
      <a class="mcrz-href-primary"
         target="_blank"
         :href="`https://viaf.org/viaf/${display_details.viaf_identifier}/`">
        {{ $gettext('VIAF: %1', display_details.viaf_identifier) }}
      </a>
    </div>
    <div v-if="display_details.canonical" class="font-bold text-gray-500">
      {{ $gettext('See “%1”', display_details.canonical.name) }}
    </div>
    <div class="flex" v-if="!agent.canonical && can_edit">
      <span @click="edit_agent" class="text-spectra-600 cursor-pointer
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
        <div class="mt-1">
          <label class="mcrz-label"
                 :for="`agent_first_name_${agent.id}`">
            {{ $gettext('First Name') }}</label>
          <div class="flex">
            <input class="mcrz-input"
                   v-model="agent_editable_data.first_name"
                   :id="`agent_first_name_${agent.id}`" />
          </div>
        </div>
        <div class="mt-1">
          <label class="mcrz-label"
                 :for="`agent_middle_name_${agent.id}`">
            {{ $gettext('Middle Name') }}</label>
          <div class="flex">
            <input class="mcrz-input"
                   v-model="agent_editable_data.middle_name"
                   :id="`agent_middle_name_${agent.id}`" />
          </div>
        </div>
        <div class="mt-1">
          <label class="mcrz-label"
                 :for="`agent_last_name_${agent.id}`">
            {{ $gettext('Last Name') }}</label>
          <div class="flex">
            <input class="mcrz-input"
                   v-model="agent_editable_data.last_name"
                   :id="`agent_last_name_${agent.id}`" />
          </div>
        </div>
        <div class="mt-1">
          <label class="mcrz-label"
                 :for="`agent_place_of_birth_${agent.id}`">
            {{ $gettext('Place of Birth') }}</label>
          <div class="flex">
            <input class="mcrz-input"
                   v-model="agent_editable_data.place_of_birth"
                   :id="`agent_place_of_birth_${agent.id}`" />
          </div>
        </div>

        <div class="mt-1">
          <label class="mcrz-label"
                 :for="`agent_date_of_birth_${agent.id}`">
            {{ $gettext('Year of Birth') }}</label>
          <div class="flex">
            <input class="mcrz-input"
                   type="number" :max="new Date().getFullYear()" step="1"
                   v-model="agent_editable_data.date_of_birth"
                   :id="`agent_date_of_birth_${agent.id}`" />
          </div>
        </div>

        <div class="mt-1">
          <label class="mcrz-label"
                 :for="`agent_place_of_death_${agent.id}`">
            {{ $gettext('Place of Death') }}</label>
          <div class="flex">
            <input class="mcrz-input"
                   v-model="agent_editable_data.place_of_death"
                   :id="`agent_place_of_death_${agent.id}`" />
          </div>
        </div>

        <div class="mt-1">
          <label class="mcrz-label"
                 :for="`agent_date_of_death_${agent.id}`">
            {{ $gettext('Year of Death') }}</label>
          <div class="flex">
            <input class="mcrz-input"
                   type="number" :max="new Date().getFullYear()" step="1"
                   v-model="agent_editable_data.date_of_death"
                   :id="`agent_date_of_death_${agent.id}`" />
          </div>
        </div>


        <div class="mt-1">
          <label class="mcrz-label" :for="`agent-first-name-${agent.id}`">{{ $gettext('VIAF Identifier') }}</label>
          <div class="flex">
            <input type="number"
                   step="1"
                   class="mcrz-input" v-model="agent_editable_data.viaf_identifier"
                   :id="`agent-first-name-${agent.id}`" />
          </div>
        </div>
        <div class="mt-1">
          <label class="mcrz-label" :for="`agent-wikidata-id-${agent.id}`">{{ $gettext('WikiData ID') }}</label>
          <div class="flex">
            <input type="text"
                   class="mcrz-input" v-model="agent_editable_data.wikidata_id"
                   :id="`agent-wikidata-id-${agent.id}`" />
          </div>
        </div>

        <button class="btn-primary my-2 p-1" type="submit">
          {{ $gettext('Submit') }}
        </button>
      </form>
    </div>
  </div>
</template>
