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
    <a :href="'/library/' + l.id">
      <span class="bg-claret-900 rounded text-white font-bold text-sm p-1 m-1">{{ l.name }}</span>
    </a>
  </span>
</template>
