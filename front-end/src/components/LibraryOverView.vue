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
                      this.libraries = res.data.libraries;
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
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
    <div class="m-1" v-for="library in libraries">
      <LibraryBox :library="library">
        <router-link class="font-bold"
                     :to="{ name: 'library_view', params: { id: library.id } }">
          <h2 class="font-bold mb-1">
            <span :class="`mcrz-library-${library.library_type || 'digital'}`">
              {{ library.name }}
            </span>
          </h2>
        </router-link>
      </LibraryBox>
    </div>
  </div>
</template>
