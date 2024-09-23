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
  <div class="mt-1 mx-2 flex flex-wrap">
    <span v-for="l in libraries">
      <router-link class="border-spectra-900 hover:border-spectra-700 border whitespace-nowrap
                          rounded text-spectra-900 hover:text-spectra-700 text-[12px] p-px m-1 leading-8"
                   :to="{ name: 'library_view', params: { id: l.id } }">
        {{ l.name }}
      </router-link>
    </span>
  </div>
</template>
