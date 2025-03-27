<script setup>
 import NavBar from '../components/NavBar.vue'
 import AgentOverView from '../components/AgentOverView.vue'
 import NavFooter from '../components/NavFooter.vue'
</script>
<template>
  <NavBar />
  <main class="grow">
    <div class="m-1 md:m-5">
      <AgentOverView />
    </div>
  </main>
  <NavFooter />
</template>
