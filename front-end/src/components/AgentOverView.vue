<script>
 import axios from 'axios'
 import MergeBox from './MergeBox.vue'
 import AgentBox from './AgentBox.vue'
 export default {
     components: {
         AgentBox,
         MergeBox,
     },
     data() {
         return {
             search_string: "",
             agents: [],
             error: null,
             warning: "",
             can_merge: false,
             matches: 0,
         }
     },
     methods: {
         get_agents() {
             this.error = null;
             if (this.search_string) {
                 axios.get('/collector/api/agents',
                           { params: { 'search': this.search_string } })
                      .then(res => {
                          this.can_merge = res.data.can_merge;
                          this.agents = [];
                          this.agents = res.data.agents;
                          this.matches = res.data.matches;
                          this.warning = res.data.warning;
                      })
                      .catch(error => {
                          this.error = error;
                      });
             }
             else {
                 console.log("get_agents called without a search");
                 this.error = null;
                 this.agents = [];
                 this.matches = 0;
                 this.warning = "Please search";
             }
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
  <div class="grid grid-cols-[auto_300px] gap-2">
    <div>
      <h1 class="font-bold text-xl text-center my-4">
        <span v-if="search_string">
          {{ $ngettext("Authors matching “%1” (%2 entry)", "Authors matching “%1” (%2 entries)", matches, search_string, matches) }}
        </span>
        <span v-else>
          {{ $gettext('Authors') }}
        </span>
      </h1>
      <div v-if="warning" class="font-bold text-center my-2">
        {{ warning }}
      </div>
      <div class="sm:flex sm:flex-nowrap sm:flex-nowrap sm:h-8 my-8">
        <input class="mcrz-input shadow w-full my-1 sm:my-0"
               v-model="search_string"
               @input="get_agents"
               :placeholder="$gettext('Type here to search authors')">
        <button
            class="btn-primary rounded-none rounded-br-3xl h-8 pr-10 pl-4 pr-10 w-full sm:w-auto"
            type="button"
            @click="get_agents">{{ $gettext('Search') }}</button>
      </div>
      <div class="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-2">
        <div class="m-1" v-for="agent in agents" :key="agent.id">
          <AgentBox :key="`${agent.id}${agent.canonical}`" :agent="agent" :can_edit="can_merge" />
        </div>
      </div>
    </div>
    <div>
      <div class="mt-16 pt-2 top-4 sticky">
        <div v-if="can_merge">
          <div id="author-cards" class="my-1">
            <MergeBox merge_type="author"
                      create_item="agent"
                      dashboard="merged-agents"
                      remove_merged_filter="creator"
                      help_text="MERGE_AUTHOR"
                      @refetch-results="get_agents">
              {{ $gettext('Merge authors here') }}
            </MergeBox>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
