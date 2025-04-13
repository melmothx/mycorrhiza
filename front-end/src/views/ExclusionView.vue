<script setup>
 import ExclusionTable from '../components/ExclusionTable.vue'
 import NavBar from '../components/NavBar.vue'
 import NavFooter from '../components/NavFooter.vue'
</script>
<template>
  <NavBar />
  <main class="grow">
    <ExclusionTable>{{ $gettext('My Exclusions') }}</ExclusionTable>
  </main>
  <NavFooter />
</template>
