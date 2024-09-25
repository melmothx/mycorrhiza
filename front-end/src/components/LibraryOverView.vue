<script>
 import LibraryBox from './LibraryBox.vue'
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     components: {
         LibraryBox,
     },
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
  <h1 class="font-bold text-4xl text-center my-4">{{ $gettext('Libraries') }}</h1>
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
    <div class="m-4" v-for="library in libraries">
      <LibraryBox :library="library">
        <h2 class="font-bold mb-1 text-xl">{{ library.name }}</h2>
      </LibraryBox>
    </div>
  </div>
</template>
