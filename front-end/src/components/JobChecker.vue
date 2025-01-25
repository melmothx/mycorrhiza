<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import {
     Cog8ToothIcon,
     ArrowPathIcon,
 } from '@heroicons/vue/24/solid'
 export default {
     components: {
         Cog8ToothIcon,
         ArrowPathIcon,
     },
     props: [ 'session_id', 'job_id' ],
     data() {
         return {
             status: "",
             error: "",
         };
     },
     methods: {
         check_job_status() {
             const jid = this.job_id;
             if (jid) {
                 const args = {
                     session_id: this.session_id,
                     action: "check_job",
                     check_job_id: jid,
                 };
                 axios.post('/collector/api/bookbuilder', args)
                      .then(res => {
                          console.log(res.data)
                          status = this.status = res.data.status
                          console.log("Status is " + status)
                          if (status == 'finished') {
                              this.error = "";
                              console.log("Finished");
                          }
                          else if (status == 'failed') {
                              this.error = "Job failed";
                          }
                          else if (status == 'not found') {
                              this.error = "Job not found. Stale session?";
                          }
                          else if (status == 'active' || status == 'inactive') {
                              console.log("Repeating it and checking " + jid),
                              setTimeout(() => { this.check_job_status() }, 1000);
                          }
                      });
             }
         },
         download_url() {
             return '/collector/api/bookbuilder/' + this.session_id;
         },
         pdf_reader() {
             return '/pdfjs/web/viewer.html?file=' + this.download_url();
         },
     },
     mounted() {
         console.log(`Mounted job checker with ${this.job_id} ${this.session_id}`);
         this.check_job_status();
     },
 }
</script>
<template>
  <div class="my-4">
    <div v-if="status == 'failed'">
      <button class="btn-primary m-1 px-4 py-1 rounded shadow-lg">
        {{ $gettext('Failed') }}
      </button>
    </div>
    <div v-if="status == 'inactive'">
      <button class="btn-accent m-1 px-4 py-1 rounded shadow-lg">
        <span class="flex items-center">
          <ArrowPathIcon class="h-4 w-4 mr-1 animate-spin" />
          {{ $gettext('Queued') }}
        </span>
      </button>
    </div>
    <div v-if="status == 'active'">
      <button type="button" class="btn-accent m-1 px-4 py-1 rounded shadow-lg">
        <span class="flex items-center">
          <Cog8ToothIcon class="h-4 w-4 mr-1 animate-spin" />
          {{ $gettext('Working') }}
        </span>
      </button>
    </div>
  </div>
  <div class="my-4" v-if="status == 'finished'">
    <iframe :src="pdf_reader()" class="w-full h-96"></iframe>
  </div>
</template>
