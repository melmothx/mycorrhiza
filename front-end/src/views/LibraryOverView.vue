<script setup>
 import NavFooter from '../components/NavFooter.vue'
 import NavBar from '../components/NavBar.vue'
 import LibraryOverView from '../components/LibraryOverView.vue'
</script>
<template>
  <NavBar />
  <main class="grow">
    <div class="m-1 md:m-5">
      <LibraryOverView />
    </div>
  </main>
  <NavFooter />
</template>
