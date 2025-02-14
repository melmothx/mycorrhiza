<script>
 import BugReport from './BugReport.vue'
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     components: {
         BugReport,
     },
     data() {
         return {
             pages: [],
         }
     },
     methods: {
         get_site_pages() {
             axios.get('/collector/api/pages/footer/' + this.$getlanguage())
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
  <footer class="mt-8 p-4 bg-gradient-to-tr from-old-copper-200 to-old-copper-300">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2">
      <div class="m-2">
        <BugReport />
      </div>
      <div v-for="page in pages" class="m-2">
        <router-link class="hover:text-old-copper-900" :to="{ name: 'page_view', params: { id: page.id } }">
          <strong>{{ page.title }}</strong>
          <div>{{ page.summary }}</div>
        </router-link>
      </div>
    </div>
  </footer>
</template>
