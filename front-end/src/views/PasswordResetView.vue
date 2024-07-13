<script setup>
 import NavBar from '../components/NavBar.vue'
 import PasswordReset from '../components/PasswordReset.vue'
</script>
<template>
  <main>
    <NavBar />
    <PasswordReset :username="$route.params.username" :token="$route.params.token" />
  </main>
</template>
