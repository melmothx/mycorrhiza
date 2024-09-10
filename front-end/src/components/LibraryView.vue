<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     props: [ "library_id" ],
     data() {
         return {
             library: null,
             error: null,
         }
     },
     methods: {
         get_library() {
             axios.get('/collector/api/libraries/' + this.library_id)
                  .then(res => {
                      this.error = null;
                      this.library = res.data.library;
                  })
                  .catch(error => {
                      this.error = error;
                  });
         }
     },
     mounted() {
         this.get_library();
     }
 }
</script>
<template>
  <div v-if="error" class="py-2 text-claret-900 font-bold">
    {{ $gettext(error) }}
  </div>
  <div v-if="library">
    <h1 class="font-bold text-xl mb-2">{{ library.name }}</h1>
    <div v-if="library.url">
      <a class="text-claret-900 font-bold hover:underline" :href="library.url">{{ $gettext('Visit Library Homepage') }}</a>
    </div>
    <div>
      <a class="text-claret-900 font-bold hover:underline"
         :href="`/library/${library.id}/entries`">
         {{ $gettext('See all entries') }}
      </a>
    </div>
    <div v-if="library.opening_hours">
      <h2 class="font-bold">{{ $gettext('Opening Hours') }}</h2>
      <div>
        {{ library.opening_hours }}
      </div>
    </div>
    <div class="my-5">
      <router-link class="text-claret-900 font-bold hover:underline"
                   :to="{ name: 'library_overview' }">
        {{ $gettext('See all libraries') }}
      </router-link>
    </div>
  </div>
</template>
