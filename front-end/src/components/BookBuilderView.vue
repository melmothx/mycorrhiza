<script>
 import axios from 'axios'
 import { bookbuilder } from '../stores/bookbuilder.js'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     data() {
         return {
             bookbuilder
         }
     },
     methods: {
         refresh_list() {
             let args = {
                 session_id: this.bookbuilder.session_id,
                 list: true,
             };
             axios.post('/collector/api/bookbuilder', args)
                  .then(res => {
                      console.log(res.data)
                      if (res.data.texts) {
                          this.bookbuilder.session_id = res.data.session_id;
                          this.bookbuilder.text_list = res.data.texts
                      }
                  });
         },
         build() {
             let args = {
                 session_id: this.bookbuilder.session_id,
                 build: true,
             };
             axios.post('/collector/api/bookbuilder', args)
                  .then(res => {
                      console.log(res.data)
                  });
         },
     },
     mounted() {
         this.refresh_list();
     },
 }
</script>
<template>
  <div v-for="text in bookbuilder.text_list" :key="text.sid + text.id">
    <div class="font-bold">{{ text.title }}</div>
  </div>
  <div v-if="bookbuilder.text_list.length > 0">
    <button class="btn-accent m-1 px-4 py-1 rounded shadow-lg" @click="build">
      {{ $gettext('Build') }}
    </button>
  </div>
</template>
