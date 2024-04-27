<script setup>
 import EntryPage from '../components/EntryPage.vue'
 import NavBar from '../components/NavBar.vue'
</script>

<template>
  <main>
    <NavBar />
    <EntryPage :entry_id="$route.params.id" />
  </main>
</template>
