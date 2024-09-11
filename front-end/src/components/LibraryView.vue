<script>
 import LibraryBox from './LibraryBox.vue'
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     props: [ "library_id" ],
     components: {
         LibraryBox,
     },
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
  <LibraryBox :library="library" :full="true">
  </LibraryBox>
  <div class="my-5">
    <router-link class="text-claret-900 font-bold hover:text-claret-700"
                 :to="{ name: 'library_overview' }">
      {{ $gettext('See all libraries') }}
    </router-link>
  </div>
</template>
