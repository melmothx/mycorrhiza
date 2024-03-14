<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>
<template>
  <router-view v-slot="{ Component }">
    <keep-alive include="home">
      <component :is="Component" />
    </keep-alive>
  </router-view>
</template>

