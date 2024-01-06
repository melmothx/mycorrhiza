<script setup>
 import EntryPage from '../components/EntryPage.vue'
</script>

<template>
  <main>
    <EntryPage :entry_id="$route.params.id" />
  </main>
</template>
