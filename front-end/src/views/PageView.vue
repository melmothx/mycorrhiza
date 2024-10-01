<script setup>
 import NavBar from '../components/NavBar.vue'
 import PageView from '../components/PageView.vue'
 import NavFooter from '../components/NavFooter.vue'
</script>
<template>
  <NavBar />
  <main class="flex-grow">
    <div class="m-1 md:m-5">
      <PageView :page_id="$route.params.id" />
    </div>
  </main>
  <NavFooter />
</template>
