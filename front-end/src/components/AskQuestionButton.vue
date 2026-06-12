<script>
 import axios from 'axios'
 import { QuestionMarkCircleIcon } from '@heroicons/vue/24/solid'
 export default {
     components: { QuestionMarkCircleIcon },
     props: [
         'data_source_id',
     ],
     emits: [
         'questionAsked',
     ],
     data() {
         return {
             open: false,
             question: "",
             working: false,
         }
     },
     methods: {
         ask_question() {
             const vm = this;
             const params = {
                 "question": vm.question,
                 "data_source_id": vm.data_source_id,
             };
             const opts = {
                 "xsrfCookieName": "csrftoken",
                 "xsrfHeaderName": "X-CSRFToken",
             };
             vm.working = true;
             axios.post('/collector/api/questions', params, opts)
                  .then(function(res) {
                      console.log(res.data)
                      vm.working = false;
                      vm.close_dialog();
                      vm.$emit('questionAsked');
                  })
                  .catch(function(error) {
                      console.log(error)
                      vm.working = false;
                  });
         },
         open_dialog() {
             this.open = true;
         },
         close_dialog() {
             this.question = "";
             this.open = false;
         }
     }
 }
</script>
<template>
  <span class="cursor-pointer text-spectra-700 hover:text-spectra-600 text-lg"
        :title="$gettext('Ask something')"
        @click="open_dialog">
    <QuestionMarkCircleIcon class="w-4 h-4 m-1" />
  </span>

  <div v-if="open">
    <div class="fixed inset-0 z-10 w-screen overflow-y-auto font-normal font-serif">
      <div class="flex min-h-full items-center justify-center text-center p-4">
        <div class="border rounded-lg bg-white text-left shadow">
          <div class="bg-gradient-to-r from-spectra-700 to-spectra-600 px-4 pb-4 pt-5">
            <div class="mt-3 text-center">
              <h3 class="text-base font-semibold leading-6 text-white">
                {{ $gettext('Ask a question') }}
              </h3>
              <div class="mt-2">
                <textarea v-model="question"
                          :placeholder="$gettext('Your question')"
                          class="rounded border-gray-300 focus:ring-0 active:ring-0 active:border-gray-300 focus:border-gray-300 w-full">
                </textarea>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 flex">
            <button type="button" class="inline-flex w-full justify-center rounded-md border m-1
                          hover:border-spectra-700"
                    @click="close_dialog"
                    :disabled="working">
              {{ $gettext('Cancel') }}
            </button>
            <button v-if="question && !working"
                    type="button" class="inline-flex w-full justify-center rounded-md border m-1
                          hover:border-spectra-700"
                    @click="ask_question">
              {{ $gettext('Ask') }}
            </button>
            <button v-if="working"
                    type="button" class="inline-flex w-full justify-center rounded-md border m-1
                          hover:border-spectra-700 cursor-wait"
                    disabled>
              <span class="animate-ping">{{ $gettext('Working') }}</span>
            </button>
          </div>
        </div>
        <div>
        </div>
      </div>
    </div>
  </div>
</template>
