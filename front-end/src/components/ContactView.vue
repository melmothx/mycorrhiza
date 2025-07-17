<script>
 import Axios from 'axios'
 import { setupCache } from 'axios-cache-interceptor';
 const instance = Axios.create();
 const caxios = setupCache(instance);
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
                       console.log(res.data);
                       if (res.data) {
                           this.settings = res.data;
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
  <h1 class="font-bold mx-auto text-xl text-center my-8">
    {{ settings.site_name }} <br>
    {{ $gettext('Contacts') }}
  </h1>
  <div class="mcrz-text-box text-center">
    <div v-if="settings.contact_email">
      <p>
        {{ $gettext('Feel free to reach out to us at:') }}
        <a class="mcrz-link" :href="'mailto:' + settings.contact_email">{{ settings.contact_email }}</a>
      </p>
    </div>
    <div v-else>
      {{ $gettext('This project has no contact email. Please check the footer instead') }}
    </div>
  </div>
</template>
