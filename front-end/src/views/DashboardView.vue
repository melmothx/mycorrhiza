<script setup>
 import DashboardTable from '../components/DashboardTable.vue'
 import NavBar from '../components/NavBar.vue'
</script>
<template>
  <main>
    <NavBar />
    <div class="m-5 p-2">
      <div class="flex">
        <div class="flex-grow">
          <h1 class="capitalize bold text-lg text-center font-bold mb-8">
            {{ $gettext('dashboard for ' + $route.params.type) }}
          </h1>
        </div>
        <div>
          <button class="btn-primary rounded-br-3xl h-8 pr-10 pl-4 pr-10"
                  type="button" @click="$router.go(-1)">{{ $gettext('Back') }}</button>
        </div>
      </div>
      <DashboardTable :listing_url="'/collector/api/listing/' + $route.params.type"
                      :removal_url="'/collector/api/revert/' + $route.params.type"
                      :key="$route.params.type" />
    </div>
  </main>
</template>
