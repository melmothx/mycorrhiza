<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     data() {
         return {
             message: null,
             open: false,
             message_sent: false,
             message_failure: null,
             email_from: null,
             current_page: window.location.href,
         }
     },
     mounted() {
         axios.get('/collector/api/auth/user').then(res => {
             this.email_from = res.data.email;
         });
     },
     methods: {
         toggle_dialog() {
             this.open = !this.open;
             this.current_page = window.location.href;
         },
         close_dialog() {
             this.open = false;
         },
         send_message() {
             this.message_failure = null;
             axios.post('/collector/api/report/bug',
                        {
                            message: "On " + this.current_page + "\n\nFrom " + this.email_from + "\n\n" + this.message,
                            email_from: this.email_from,
                        })
                  .then(res => {
                      console.log(res.data);
                      if (res.data.success) {
                          this.close_dialog();
                          this.message = "";
                          this.message_sent = true;
                      }
                      else {
                          this.message_failure = res.data.error || "Error";
                      }
                  })
                  .catch(error => {
                      this.message_failure = error;
                  });
             ;
         }
     }
 }
</script>
<template>
  <button class="btn-accent text-sm px-4 py-1 rounded-sm shadow-lg" @click="toggle_dialog">
    <template v-if="message_sent">
      {{ $gettext('Report Sent') }}
    </template>
    <template v-else>
      {{ $gettext('Bug Report') }}
    </template>
  </button>
  <div v-if="open">
    <div class="fixed inset-x-0 top-0 overflow-y-auto font-normal">
      <div class="flex items-center justify-center p-4">
        <div class="mx-8 mt-8 p-8 w-1/2 border border-perl-bush-200 text-black bg-perl-bush-100 shadow-lg">
          <h2 class="font-bold text-lg text-center">
            {{ $gettext('Report a bug to the site administrators') }}
          </h2>
          <div class="px-4 pb-4 pt-5 flex items-center">
            <span class="font-bold mr-2">{{ $gettext('From:') }}</span>
            <input class="mcrz-input w-full"
                   type="text"
                   placeholder="my-email@example.com"
                   v-model="email_from" />
          </div>
          <div class="px-4 pb-2 pt-2 flex items-center">
            <span class="font-bold mr-2">{{ $gettext('Page:') }}</span>
            <span> {{ current_page }}</span>
          </div>
          <div class="px-4 pb-4 pt-5">
            <textarea class="mcrz-textarea w-full h-64" v-model="message"></textarea>
          </div>
          <div v-if="message_failure" class="text-cab-sav-800 font-bold text-center m-3">
            <div>
              {{ $gettext('Failure sending the report. Please contact us by email!') }}
            </div>
            <div>
              {{ message_failure }}
            </div>
          </div>

          <div class="text-center">
            <button v-if="message && email_from" class="btn-accent p-2 mx-2 rounded-sm" @click="send_message">
              {{ $gettext('Send') }}
            </button>
            <button class="btn-primary p-2 mx-2 rounded-sm" @click="close_dialog">
              {{ $gettext('Cancel') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>
