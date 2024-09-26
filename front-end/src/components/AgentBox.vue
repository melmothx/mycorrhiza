<script>
 export default {
     props: [ "agent" ],
 }
</script>
<template>
  <div v-if="agent" class="border border-perl-bush-200 bg-perl-bush-50 p-1 shadow">
    <a :href="`/library/author/${agent.search_link_id}`">
      <h2 class="font-bold">{{ agent.name }}</h2>
    </a>
    <div v-if="agent.first_name">
      {{ $gettext('First Name: %1', agent.first_name) }}
    </div>
    <div v-if="agent.last_name">
      {{ $gettext('Last Name: %1', agent.last_name) }}
    </div>
    <div v-if="agent.description" class="my-2" >
      {{ agent.description }}
    </div>
  </div>
</template>
