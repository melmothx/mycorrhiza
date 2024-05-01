<script setup>
 import DashboardTable from '../components/DashboardTable.vue'
 import NavBar from '../components/NavBar.vue'
</script>
<template>
  <main>
    <NavBar />
    <DashboardTable :listing_type="$route.params.type" :key="$route.params.type">
      {{ $gettext('dashboard for ' + $route.params.type) }}
    </DashboardTable>
  </main>
</template>
