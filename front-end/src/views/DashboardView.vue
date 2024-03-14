<script setup>
 import DashboardTable from '../components/DashboardTable.vue'
 import NavBar from '../components/NavBar.vue'
</script>
<template>
  <main>
    <NavBar />
    <DashboardTable :listing_type="$route.params.type">
      <div v-if="$route.params.type == 'exclusions'">
        {{ $gettext('Exclusions') }}
      </div>
      <div v-if="$route.params.type == 'merged-entries'">
        {{ $gettext('Merged Entries') }}
      </div>
      <div v-if="$route.params.type == 'merged-agents'">
        {{ $gettext('Merged Agents') }}
      </div>
    </DashboardTable>
  </main>
</template>
