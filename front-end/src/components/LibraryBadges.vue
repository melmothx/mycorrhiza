<script>
 import Axios from 'axios';
 import { setupCache } from 'axios-cache-interceptor';
 const instance = Axios.create();
 const caxios = setupCache(instance)
 export default {
     props: [ 'data_sources' ],
     data() {
         return {
             libraries: [],
         }
     },
     methods: {
         get_library_details() {
             /* cached request */
             caxios.get('/collector/api/libraries')
                   .then(res => {
                       const libs = {};
                       res.data.libraries.forEach((l, i) => {
                           libs[l.id] = l;
                       });
                       this.libraries =
                           [ ...new Map(this.data_sources.map(v => [ v.library_id,
                                                                     { id: v.library_id,
                                                                       details: libs[v.library_id],
                                                                     } ])).values() ];
                   })
                   .catch(error => {
                       console.log(error);
                   });
         }
     },
     mounted() {
         this.get_library_details();
     },
 }
</script>
<template>
  <div class="mt-1 mx-2 flex flex-wrap">
    <span v-for="l in libraries">
      <router-link :class="`mcrz-micro-badge mcrz-library-${l.details.library_type || 'digital'}`"
                   :to="{ name: 'library_view', params: { id: l.id } }">
        {{ l.details.name }}
      </router-link>
    </span>
  </div>
</template>
