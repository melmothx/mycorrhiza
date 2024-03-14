<script setup>
 import ExclusionTable from '../components/ExclusionTable.vue'
 import NavBar from '../components/NavBar.vue'
</script>
<template>
  <main>
    <NavBar />
    <ExclusionTable>{{ $gettext('My Exclusions') }}</ExclusionTable>
  </main>
</template>
