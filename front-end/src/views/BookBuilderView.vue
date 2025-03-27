<script setup>
 import NavBar from '../components/NavBar.vue'
 import BookBuilderView from '../components/BookBuilderView.vue'
 import NavFooter from '../components/NavFooter.vue'
</script>
<template>
  <NavBar />
  <main class="grow">
    <div class="m-1 md:m-5">
      <BookBuilderView />
    </div>
  </main>
  <NavFooter />
</template>
