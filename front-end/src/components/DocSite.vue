<script>
 import Axios from 'axios';
 import { setupCache } from 'axios-cache-interceptor';
 const instance = Axios.create();
 const caxios = setupCache(instance)
 export default {
     data() {
         return {
             amusewiki_doc_site: null,
         }
     },
     methods: {
         get_site_config() {
             caxios.get('/collector/api/general')
                   .then(res => {
                       if (res.data) {
                           if (res.data.amusewiki_doc_site) {
                               this.amusewiki_doc_site = res.data.amusewiki_doc_site + '/localized?__language=' + this.$getlanguage();
                           }
                       }
                   })
                   .catch(error => {
                       console.log(error);
                   });
         },
     },
     mounted() {
         this.get_site_config();
     },
 }
</script>
<template>
  <a v-if="amusewiki_doc_site"  :href="amusewiki_doc_site">
    <div class="btn-accent text-sm p-2 mx-4 rounded-sm shadow-lg text-center">
      {{ $gettext('Documentation') }}
    </div>
  </a>
</template>
