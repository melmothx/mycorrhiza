<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import {
     PencilSquareIcon,
     HandRaisedIcon,
 } from '@heroicons/vue/24/solid'
 export default {
     props: [ "agent", "can_edit", "short", "get_wikidata" ],
     data() {
         return {
             error: null,
             edited: false,
             show_editing: false,
             agent_editable_data: {},
             display_details: {},
             wikidata: null,
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
                      this.get_api_wikidata();
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
         get_api_wikidata() {
             if (this.get_wikidata) {
                 axios.get('/collector/api/agents/' + this.agent.id + '/wikidata/' + this.$getlanguage())
                      .then((res) => {
                          if (res.data) {
                              this.wikidata = res.data;
                          }
                      })
                      .catch(error => {
                          this.error = error;
                      });
             }
         },
         check_if_url(string) {
             const regex = /^https?:\/\/[^ ]+$/;
             return regex.test(string)
         }
     },
     mounted() {
         this.display_details = { ...this.agent };
         this.get_api_wikidata()
     },
 }
</script>
<template>
  <div v-if="agent" class="border border-perl-bush-200 bg-perl-bush-50 p-4 shadow-sm rounded-sm">
    <div v-if="short">
      <div v-if="wikidata">
        <a :href="wikidata.link">
          <h2 class="font-bold text-lg mb-4 border-b border-old-coper-100">{{ wikidata.name }}</h2>
        </a>
      </div>
      <div v-else>
        <h2 class="font-bold text-lg mb-4 border-b border-old-coper-100">{{ agent.name }}</h2>
      </div>
      <div v-if="wikidata && wikidata.statements">
        <div v-for="ws in wikidata.statements" :key="ws.property">

          <div v-if="ws.data_type == 'commonsMedia'">
            <div v-for="wsv in ws.values">
              <div v-if="wikidata.link">
                <a :href="wikidata.link">
                  <img :src="wsv" />
                </a>
              </div>
              <div v-else>
                <img :src="wsw" />
              </div>
            </div>
          </div>
          <div v-else>
            <h3 class="font-bold">{{ ws.name }}</h3>
            <div v-for="wsv in ws.values">
              <p v-if="check_if_url(wsv)">
                <a class="mcrz-href-normal" :href="wsv">{{ wsv }}</a>
              </p>
              <p v-else>
                {{ wsv }}
              </p>
            </div>
          </div>
        </div>
        <div class="my-3 text-sm">
          <a :href="`https://www.wikidata.org/wiki/${agent.wikidata_id}`"
            class="mcrz-href-normal">
            {{ $gettext('Source: Wikidata') }}
          </a>
        </div>
      </div>
    </div>
    <div v-else>
      <a :href="`/library/author/${agent.search_link_id}`" target="_blank">
        <h2 class="font-bold">{{ agent.name }}</h2>
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
