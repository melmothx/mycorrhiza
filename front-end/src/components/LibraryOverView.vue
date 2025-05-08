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
             filtered_libraries: [],
             error: null,
             query: null,
         }
     },
     methods: {
         get_libraries() {
             axios.get('/collector/api/libraries')
                  .then(res => {
                      this.error = null;
                      this.libraries = this.filtered_libraries = res.data.libraries;
                  })
                  .catch(error => {
                      this.error = error;
                  });
         },
         filter_libraries() {
             console.log(`Search ${this.query}`);
             const search = this.query.normalize("NFKD").replace(/\p{Mn}/gu, "").toLowerCase();
             this.filtered_libraries = this.libraries.filter((l) => {
                 for (const k in l) {
                     if (typeof l[k] === "string") {
                         if (l[k].normalize("NFKD").replace(/\p{Mn}/gu, "")
                                 .toLowerCase().includes(search)) {
                             return true;
                         }
                     }
                 }
                 return false;
             })
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
  <div class="sm:flex sm:flex-nowrap sm:flex-nowrap sm:h-8 my-8">
    <input class="mcrz-input shadow-sm w-full my-1 sm:my-0"
           v-model="query"
           @input="filter_libraries"
           :placeholder="$gettext('Type here to search the libraries')">
  </div>
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
    <div class="m-1" v-for="library in filtered_libraries">
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
