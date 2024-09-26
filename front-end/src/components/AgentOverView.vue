<script>
 import axios from 'axios'
 import AgentBox from './AgentBox.vue'
 export default {
     components: {
         AgentBox,
     },
     data() {
         return {
             agents: [],
             error: null,
         }
     },
     methods: {
         get_agents() {
             axios.get('/collector/api/agents')
                  .then(res => {
                      this.error = null;
                      this.agents = res.data.agents;
                  })
                  .catch(error => {
                      this.error = error;
                  });
         },
     },
     mounted() {
         this.get_agents();
     },
 } 
</script>
<template>
  <div v-if="error" class="py-2 text-claret-900 font-bold">
    {{ $gettext(error) }}
  </div>
  <h1 class="font-bold text-4xl text-center my-4">{{ $gettext('Authors') }}</h1>
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
    <div class="m-1" v-for="agent in agents">
      <AgentBox :agent="agent" />
    </div>
  </div>
</template>
