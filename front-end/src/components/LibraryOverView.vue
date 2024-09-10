<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     data() {
         return {
             libraries: [],
             error: null,
         }
     },
     methods: {
         get_libraries() {
             axios.get('/collector/api/libraries')
                  .then(res => {
                      this.error = null;
                      this.libraries = res.data.libraries
                  })
                  .catch(error => {
                      this.error = error;
                  });
         },
     },
     mounted() {
         console.log("Mounted the libraries");
         this.get_libraries();
     }
 }
</script>
<template>
  <div v-if="error" class="py-2 text-claret-900 font-bold">
    {{ $gettext(error) }}
  </div>
  <h1 class="font-bold text-2xl text-center mb-2">{{ $gettext('Our libraries') }}</h1>
  <div class="grid grid-cols-4 gap-4">
    <div class="m-4" v-for="library in libraries">
      <h2 class="font-bold">
        {{ library.name }}
      </h2>
      <div v-if="library.url">
        <a class="text-claret-900 font-bold hover:underline" :href="library.url">{{ $gettext('Visit Library Homepage') }}</a>
      </div>
      <div>
        <a class="text-claret-900 font-bold hover:underline"
           :href="`/library/${library.id}/entries`">
          {{ $gettext('See all entries') }}
        </a>
      </div>
    </div>
  </div>
</template>
