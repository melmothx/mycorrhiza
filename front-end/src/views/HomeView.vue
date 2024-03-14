<script>
 import { ref } from 'vue'
 import NavBar from '../components/NavBar.vue'
 import SearchPage from '../components/SearchPage.vue'
 export default {
     name: "home",
     components: { NavBar, SearchPage },
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
     },
 }
</script>

<template>
  <nav>
    <NavBar @refetch-results="refetch_results" />
  </nav>
  <main>
    <SearchPage ref="search_page" />
  </main>
</template>
