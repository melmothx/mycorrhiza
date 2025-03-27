<script setup>
 import NavBar from '../components/NavBar.vue'
 import NavFooter from '../components/NavFooter.vue'
 import PasswordReset from '../components/PasswordReset.vue'
</script>
<template>
  <NavBar />
  <main class="grow">
    <PasswordReset :username="$route.params.username" :token="$route.params.token" />
  </main>
  <NavFooter />
</template>
