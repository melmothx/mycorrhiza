<script setup>
 import EntryPage from '../components/EntryPage.vue'
 import NavBar from '../components/NavBar.vue'
 import NavFooter from '../components/NavFooter.vue'
</script>

<template>
  <NavBar />
  <main class="grow">
    <EntryPage :entry_id="$route.params.id" />
  </main>
  <NavFooter />
</template>
