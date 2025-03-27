<script>
 import { ref } from 'vue'
 import NavBar from '../components/NavBar.vue'
 import NavFooter from '../components/NavFooter.vue'
 import SearchPage from '../components/SearchPage.vue'
 export default {
     name: "search",
     components: { NavBar, SearchPage, NavFooter },
     setup() {
         const search_page = ref(null)
         return {
             search_page
         }
     },
     methods: {
         refetch_results() {
             this.search_page.getResults({ update_facets: 1 });
         },
     },
 }
</script>

<template>
  <NavBar @refetch-results="refetch_results" />
  <main class="grow">
    <SearchPage ref="search_page" />
  </main>
  <NavFooter />
</template>
