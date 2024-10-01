<script setup>
 import BackButton from '../components/BackButton.vue'
 import DashboardTable from '../components/DashboardTable.vue'
 import NavBar from '../components/NavBar.vue'
 import NavFooter from '../components/NavFooter.vue'
</script>
<template>
  <NavBar />
  <main class="flex-grow">
    <div class="m-5 p-2">
      <div class="flex">
        <div class="flex-grow">
          <h1 class="capitalize bold text-lg text-center font-bold mb-8">
            {{ $gettext('dashboard for ' + $route.params.type) }}
          </h1>
        </div>
        <div>
          <BackButton />
        </div>
      </div>
      <DashboardTable :listing_url="'/collector/api/listing/' + $route.params.type"
                      :removal_url="'/collector/api/revert/' + $route.params.type"
                      :key="$route.params.type" />
    </div>
  </main>
  <NavFooter />
</template>
