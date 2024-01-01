<script>
 import { ref } from 'vue'
 import NavBar from './components/NavBar.vue'
 import SearchPage from './components/SearchPage.vue'
 import EntryPage from './components/EntryPage.vue'
 export default {
     components: { NavBar, SearchPage, EntryPage },
     data() {
         return {
             entry_id: 0,
         }
     },
     setup() {
         const search_page = ref(null)
         return {
             search_page
         }
     },
     methods: {
         refetch_results() {
             this.search_page.getResults(1);
         },
         set_entry_id(id) {
             console.log("Setting entry:" + id);
             this.entry_id = id;
         }
     },
 }
</script>

<template>
  <NavBar @refetch-results="refetch_results" />
  <div v-if="entry_id">
    <EntryPage :entry_id="entry_id"
               @close="set_entry_id(0)"
               @change-id="set_entry_id"
    />
  </div>
  <div>
    <SearchPage ref="search_page" @set-entry-id="set_entry_id" />
  </div>
</template>

