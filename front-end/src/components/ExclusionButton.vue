<script>
 import axios from 'axios'
 export default {
     props: [
         'object_id',
         'object_type',
     ],
     emits: [
         'refetchResults',
     ],
     data() {
         return {
             comment: "Trashed",
         }
     },
     methods: {
         set_exclusion() {
             const vm = this;
             const params = {
                 "op": "add",
                 "comment": vm.comment,
                 "id": vm.object_id,
                 "type": vm.object_type,
             };
             const opts = {
                 "xsrfCookieName": "csrftoken",
                 "xsrfHeaderName": "X-CSRFToken",
             };
             axios.post('/search/api/exclusions', params, opts)
                  .then(function(res) {
                      console.log(res.data)
                      vm.$emit('refetchResults');
                  })
                  .catch(function(error) {
                      console.log(error)
                  });
         },
     }
 }
</script>
<template>
  <span class="text-sm" @click="set_exclusion">Trash</span>
</template>
