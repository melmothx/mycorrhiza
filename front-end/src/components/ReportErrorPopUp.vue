<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     props: [
         'data_source_id',
         'library_name',
     ],
     data() {
         return {
             user_data: {},
             message: null,
             open: false,
             message_sent: false,
             message_failure: false,
         }
     },
     mounted() {
         axios.get('/collector/api/auth/user').then(res => {
             this.user_data = res.data;
             console.log("Checking user data");
             console.log(this.user_data.logged_in)
         });
     },
     methods: {
         toggle_dialog() {
             this.open = !this.open;
         },
         close_dialog() {
             this.open = false;
         },
         send_message() {
             console.log(this.message);
             this.message_failure = false;
             this.message_sent = true;
             this.close_dialog();
             axios.post('/collector/api/report/data-source-error/' + this.data_source_id,
                        { message: this.message })
                  .then(res => {
                      console.log(res.data);
                      if (res.data.success) {
                          this.message = "";
                          this.message_sent = true;
                      }
                      else {
                          this.message_failure = true;
                      }
                  });
         }
     }
 }
</script>
<template>
  <div v-if="user_data.logged_in && user_data.email && !message_sent">
    <button class="btn-accent m-1 px-4 py-1 rounded shadow-lg" @click="toggle_dialog">
      {{ $gettext('Report Error') }}
    </button>
  </div>
  <div v-if="message_sent">
    <button class="btn-primary m-1 px-4 py-1 rounded shadow-lg">
      {{ $gettext('Report Sent!') }}
    </button>
  </div>
  <div v-if="message_failure">
    <button class="btn-accent m-1 px-4 py-1 rounded shadow-lg">
      {{ $gettext('Failure sending the report. Please contact us by email!') }}
    </button>
  </div>
  <div v-if="open">
    <div class="fixed inset-x-0 top-0 overflow-y-auto font-normal">
      <div class="flex items-center justify-center p-4">
        <div class="mx-8 mt-16 p-8 w-1/2 border border-perl-bush-200 text-black shadow-lg bg-perl-bush-100 shadow-lg">
          <h2 class="font-bold text-lg text-center">{{ $gettext('Report an error to %1', library_name) }}</h2>
          <div class="px-4 pb-4 pt-5">
            <textarea class="mcrz-textarea w-full h-64" v-model="message"></textarea>
          </div>
          <div class="text-center">
            <button v-if="message" class="btn-accent p-2 mx-2 rounded" @click="send_message">
              {{ $gettext('Send') }}
            </button>
            <button class="btn-primary p-2 mx-2 rounded" @click="close_dialog">
              {{ $gettext('Cancel') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>
