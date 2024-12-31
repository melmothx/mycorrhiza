<script>
 import Axios from 'axios';
 import { setupCache } from 'axios-cache-interceptor';
 const instance = Axios.create();
 const caxios = setupCache(instance)
 export default {
     data() {
         return {
             settings: {},
         }
     },
     methods: {
         get_site_config() {
             caxios.get('/collector/api/general')
                   .then(res => {
                       if (res.data) {
                           this.settings = res.data;
                           if (this.settings.site_name) {
                               document.title = this.settings.site_name;
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
  <div>
    <router-link :to="{ name: 'home' }">
      <template v-if="settings.site_logo">
        <img class="w-64" :src="settings.site_logo"
             :alt="settings.site_name || 'Home'"
             :title="settings.description || settings.site_name"
        />
      </template>
      <template v-else>
        <span>{{ settings.site_name || 'Home' }}</span>
      </template>
    </router-link>
  </div>
</template>
