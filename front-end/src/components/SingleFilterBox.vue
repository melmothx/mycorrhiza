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
                          this.agent = res.data.agent;
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
