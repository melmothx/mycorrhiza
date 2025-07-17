<script setup>
 import NavFooter from '../components/NavFooter.vue'
 import NavBar from '../components/NavBar.vue'
 import ContactView from '../components/ContactView.vue'
</script>
<template>
  <NavBar />
  <main class="grow">
    <div class="m-1 md:m-5">
      <ContactView />
    </div>
  </main>
  <NavFooter />
</template>
