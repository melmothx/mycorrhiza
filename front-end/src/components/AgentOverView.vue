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
             can_merge: false,
             all_agents: [],
         }
     },
     methods: {
         get_agents() {
             axios.get('/collector/api/agents')
                  .then(res => {
                      this.error = null;
                      this.can_merge = res.data.can_merge;
                      this.all_agents = res.data.agents;
                      this.filter_by_search();
                      console.log(res.data.can_merge);
                  })
                  .catch(error => {
                      this.error = error;
                  });
         },
         filter_by_search() {
             if (this.search_string) {
                 const search = this.search_string.toLowerCase();
                 const fields = ['fname', 'lname', 'name'];
                 this.agents = this.all_agents.filter((el) => {
                     for (const f of fields) {
                         if (el[f] && el[f].toString().toLowerCase().includes(search)) {
                             return true;
                         }
                     }
                     let canonical = el.canonical;
                     if (canonical) {
                         for (const f of fields) {
                             if (canonical[f] && canonical[f]
                                 .toString().toLowerCase().includes(search)) {
                                 return true;
                             }
                         }
                     }
                 });
             }
             else {
                 this.agents = this.all_agents.filter(() => true);
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
      <h1 class="font-bold text-4xl text-center my-4">
        <span v-if="search_string">
          {{ $gettext('Authors matching %1', search_string) }}
        </span>
        <span v-else>
          {{ $gettext('Authors') }}
        </span>
      </h1>
      <div class="grid lg:grid-cols-2 gap-2">
        <div class="m-1" v-for="agent in agents">
          <AgentBox :key="agent.id" :agent="agent" :can_edit="can_merge" />
        </div>
      </div>
    </div>
    <div>
      <div class="mt-16 pt-2 top-4 sticky">
        <div class="flex">
          <input class="mcrz-input"
                 v-model="search_string"
                 @input="filter_by_search"
                 :placeholder="$gettext('Type here to search authors')">
        </div>
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
