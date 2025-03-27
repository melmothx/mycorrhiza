<script>
 import axios from 'axios'
 import { EyeSlashIcon } from '@heroicons/vue/24/solid'
 export default {
     components: { EyeSlashIcon },
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
             axios.post('/collector/api/exclusions', params, opts)
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
  <span class="cursor-pointer text-claret-900 hover:text-claret-700 text-lg"
        :title="$gettext('Omit')"
        @click="open_dialog">
    <EyeSlashIcon class="w-4 h-4 m-1" />
  </span>

  <div v-if="open">
    <div class="fixed inset-0 z-10 w-screen overflow-y-auto font-normal font-serif">
      <div class="flex min-h-full items-center justify-center text-center p-4">
        <div class="border rounded-lg bg-white text-left shadow-sm">
          <div class="bg-white px-4 pb-4 pt-5">
            <div class="mt-3 text-center">
              <h3 class="text-base font-semibold leading-6 text-gray-900">
                <slot>{{ $gettext('Justification') }}</slot>
              </h3>
              <div class="mt-2">
                <textarea v-model="comment"
                          :placeholder="$gettext('Reason')"
                          class="rounded-sm border-gray-300 focus:ring-0 active:ring-0 active:border-gray-300  focus:border-gray-300">
                </textarea>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 flex">
            <button type="button" class="inline-flex w-full justify-center rounded-md border m-1
                          hover:border-claret-700"
                    @click="close_dialog">
              {{ $gettext('Cancel') }}
            </button>
            <button v-if="comment"
                    type="button" class="inline-flex w-full justify-center rounded-md border m-1
                          hover:border-claret-700"
                    @click="set_exclusion">
              {{ $gettext('Omit') }}
            </button>
          </div>
        </div>
        <div>
        </div>
      </div>
    </div>
  </div>
</template>
