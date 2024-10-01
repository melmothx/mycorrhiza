<script setup>
 import NavBar from '../components/NavBar.vue'
 import PageView from '../components/PageView.vue'
</script>
<template>
  <main>
    <NavBar />
    <div class="m-1 md:m-5">
      <PageView :page_id="$route.params.id" />
    </div>
  </main>
</template>
