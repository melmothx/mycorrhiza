<script>
 import LibraryBox from './LibraryBox.vue'
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     props: [ "page_id" ],
     data() {
         return {
             page: null,
         }
     },
     methods: {
         get_site_page() {
             axios.get('/collector/api/pages/' + this.page_id)
                  .then(res => {
                      this.error = null;
                      this.page = res.data.page;
                  })
                  .catch(error => {
                      this.error = error;
                  });
         },
     },
     mounted() {
         this.get_site_page();
     }
 }
</script>
<template>
  <div v-if="page && page.title">
    <h1 class="font-bold mx-auto text-xl text-center my-8">{{ page.title }}</h1>
    <div id="thework" class="mcrz-text-box" v-html="page.content">
    </div>
  </div>
</template>
