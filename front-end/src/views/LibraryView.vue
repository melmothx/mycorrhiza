<script setup>
 import NavBar from '../components/NavBar.vue'
 import NavFooter from '../components/NavFooter.vue'
 import LibraryView from '../components/LibraryView.vue' 
</script>
<template>
  <NavBar />
  <main class="grow">
    <div class="m-1 md:m-5">
      <LibraryView :library_id="$route.params.id" />
    </div>
  </main>
  <NavFooter/>
</template>
