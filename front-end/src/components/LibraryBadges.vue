<script>
 export default {
     props: [ 'data_sources' ],
     computed: {
         libraries() {
             return [ ...new Map(this.data_sources.map(v => [ v.library_id,
                                                              { id: v.library_id,
                                                                name: v.library_name
                                                              }
             ])).values() ]
         }
     }
 }
</script>
<template>
  <span v-for="l in libraries">
    <router-link class="bg-claret-900 hover:bg-claret-800
                        rounded text-white font-bold text-sm p-1 m-1"
                 :to="{ name: 'library_view', params: { id: l.id } }">
      {{ l.name }}
    </router-link>
  </span>
</template>
