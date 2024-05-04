<script>
 import axios from 'axios'
 export default {
     props: [ 'creation_type' ],
     emits: [
         'createdEntity',
     ],
     data() {
         return {
             value: null,
             flash_error: "",
         }
     },
     methods: {
         clear_flash_error() {
             this.flash_error = "";
         },
         create_aggregation() {
             if (!this.value) {
                 return;
             }
             const vm = this;
             const settings = {
                 "xsrfCookieName": "csrftoken",
                 "xsrfHeaderName": "X-CSRFToken",
             };
             const params = {
                 value: this.value,
             }
             axios.post('/collector/api/create/' + vm.creation_type, params, settings)
                  .then(function(res) {
                      if (res.data) {
                          if (res.data.created) {
                              vm.value = null;
                              vm.$emit('createdEntity', res.data.created.id, res.data.created.value);
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
  <div class="flex my-0">
    <input class="outline outline-0 border-1 border-gray-300 border-t-0
                  focus:border-gray-300 active:border-gray-300
                  w-full shrink
                  h-8 focus:ring-0 active:ring-0"
           v-model="value" />
    <button class="btn-primary rounded-none h-8 pl-3 pr-4 grow"
            @click="create_aggregation">{{ $gettext('Create') }}</button>
  </div>
  <div v-if="flash_error"
       @click="clear_flash_error"
       class="flex justify-center items-center m-2 cursor-pointer text-pink-700
             mt-2 font-semibold">
    {{ flash_error }}
  </div>
</template>
