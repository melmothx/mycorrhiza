<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     data() {
         return {
             pages: [],
         }
     },
     methods: {
         get_site_pages() {
             axios.get('/collector/api/pages')
                  .then(res => {
                      this.error = null;
                      this.pages = res.data.pages;
                  })
                  .catch(error => {
                      this.error = error;
                  });
         },
     },
     mounted() {
         this.get_site_pages();
     }
 }
</script>
<template>
  <footer>
    <div v-for="page in pages">
      <strong>{{ page.title }}</strong>
      <div>{{ page.summary }}</div>
    </div>
  </footer>
</template>
