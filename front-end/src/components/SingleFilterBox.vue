<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import LibraryBox from './LibraryBox.vue'
 import AgentBox from './AgentBox.vue'
 export default {
     props: [ "id", "name", "editable" ],
     components: {
         LibraryBox,
         AgentBox,
     },
     data() {
         return {
             agent: null,
             library: null,
         };
     },
     methods: {
         get_details() {
             if (this.name === "library") {
                 axios.get('/collector/api/libraries/' + this.id)
                      .then(res => {
                          this.error = null;
                          this.library = res.data.library;
                      })
                      .catch(error => {
                          this.error = error;
                      });
             }
             else if (this.name === "creator") {
                 axios.get('/collector/api/agents/' + this.id)
                      .then(res => {
                          this.error = null;
                          let agent = res.data.agent;
                          if (this.editable) {
                              this.agent = agent;
                          }
                          else {
                              const material = [ "first_name", "middle_name", "last_name",
                                                 "date_of_birth", "place_of_birth",
                                                 "date_of_death", "place_of_death",
                                                 "viaf_identifier"
                              ];
                              for (const value of material) {
                                  if (agent[value]) {
                                      this.agent = agent;
                                      break;
                                  }
                              }
                          }
                      })
                      .catch(error => {
                          this.error = error;
                      });

             }
         },
     },
     mounted() {
         this.get_details()
     }
 }
</script>
<template>
  <div class="my-2">
    <div v-if="agent">
      <AgentBox :agent="agent" :short="true" :can_edit="editable" />
    </div>
    <div v-if="library">
      <LibraryBox :library="library" :short="true" />
    </div>
  </div>
</template>
