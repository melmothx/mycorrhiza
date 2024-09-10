<script setup>
 import NavBar from '../components/NavBar.vue'
 import LibraryView from '../components/LibraryView.vue' 
</script>
<template>
  <main>
    <NavBar />
    <div class="m-1 md:m-5">
      <LibraryView :library_id="$route.params.id" />
    </div>
  </main>
</template>
