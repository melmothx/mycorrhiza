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
             open: false,
             comment: "",
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
                      vm.close_dialog();
                      vm.$emit('refetchResults');
                  })
                  .catch(function(error) {
                      console.log(error)
                  });
         },
         open_dialog() {
             this.open = true;
         },
         close_dialog() {
             this.comment = "";
             this.open = false;
         }
     }
 }
</script>
<template>
  <span class="text-sm cursor-pointer border-2 rounded-full px-2 bg-red-800 text-white font-semibold"
        @click="open_dialog">Omit</span>

  <div v-if="open">
    <div class="fixed inset-0 z-10 w-screen overflow-y-auto font-normal font-serif">
      <div class="flex min-h-full items-center justify-center text-center p-4">
        <div class="border rounded-lg bg-white text-left shadow">
          <div class="bg-white px-4 pb-4 pt-5">
            <div class="mt-3 text-center">
              <h3 class="text-base font-semibold leading-6 text-gray-900">Omit {{ object_type }}</h3>
              <div class="mt-2">
                <textarea v-model="comment" placeholder="Reason"
                          class="rounded border-gray-300 focus:ring-0 active:ring-0 active:border-pink-300 focus:border-pink-300">
                </textarea>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 flex">
            <button type="button" class="inline-flex w-full justify-center rounded-md border m-1"
                    @click="close_dialog">
              Cancel
            </button>
            <button v-if="comment"
                    type="button" class="inline-flex w-full justify-center rounded-md border m-1"
                    @click="set_exclusion">
              Omit
            </button>
          </div>
        </div>
        <div>
        </div>
      </div>
    </div>
  </div>
</template>
