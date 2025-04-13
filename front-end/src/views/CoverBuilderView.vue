<script setup>
 import NavBar from '../components/NavBar.vue'
 import CoverBuilderView from '../components/CoverBuilderView.vue'
 import NavFooter from '../components/NavFooter.vue'
</script>
<template>
  <NavBar />
  <main class="grow">
    <div class="m-1 md:m-5">
      <CoverBuilderView />
    </div>
  </main>
  <NavFooter />
</template>
