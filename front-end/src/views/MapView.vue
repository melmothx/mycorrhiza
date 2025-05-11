<script setup>
 import NavBar from '../components/NavBar.vue'
 import LibraryMap from '../components/LibraryMap.vue'
 import NavFooter from '../components/NavFooter.vue' 
</script>
<template>
  <NavBar />
  <main class="grow">
    <div class="m-1 md:m-5">
      <LibraryMap />
    </div>
  </main>
  <NavFooter />  
</template>
