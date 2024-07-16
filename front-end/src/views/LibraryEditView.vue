<script setup>
 import NavBar from '../components/NavBar.vue'
 import LibraryEdit from '../components/LibraryEdit.vue'
</script>
<template>
  <main>
    <NavBar />
    <LibraryEdit :library_id="$route.params.id" :key="$route.params.id" />
  </main>
</template>
