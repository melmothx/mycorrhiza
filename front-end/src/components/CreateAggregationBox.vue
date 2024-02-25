<script>
 import axios from 'axios'
 export default {
     emits: [
         'createdAggregation',
     ],
     data() {
         return {
             title: null,
             flash_error: "",
         }
     },
     methods: {
         clear_flash_error() {
             this.flash_error = "";
         },
         create_aggregation() {
             if (!this.title) {
                 return;
             }
             const vm = this;
             const settings = {
                 "xsrfCookieName": "csrftoken",
                 "xsrfHeaderName": "X-CSRFToken",
             };
             const params = {
                 title: this.title,
             }
             axios.post('/collector/api/create/aggregation', params, settings)
                  .then(function(res) {
                      if (res.data) {
                          if (res.data.created) {
                              vm.$emit('createdAggregation', res.data.created.id, res.data.created.value);
                          }
                          else {
                              vm.flash_error = res.data.error || "Failure creating entry!";
                          }
                      }
                      else {
                          vm.flash_error = "No data received";
                      }
                  });
         }
     }
 }
</script>
<template>
  <div>
    <input v-model="title" />
    <button @click="create_aggregation">Create</button>
  </div>
  <div v-if="flash_error"
       @click="clear_flash_error"
       class="flex justify-center items-center m-2 cursor-pointer text-pink-700
             mt-2 font-semibold">
    {{ flash_error }}
  </div>
</template>
