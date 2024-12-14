<script>
 import axios from 'axios'
 import { bookbuilder } from '../stores/bookbuilder.js'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import { TrashIcon, Cog8ToothIcon } from '@heroicons/vue/24/solid'
 export default {
     components: {
         TrashIcon,
         Cog8ToothIcon,
     },
     data() {
         return {
             bookbuilder
         }
     },
     methods: {
         drop_element(event, id) {
             const move_id = event.dataTransfer.getData('move_id');
             console.log(`Dropping ${move_id} into ${id}`);
         },
         drag_element(e, id) {
             console.log(`Dragging ${id}`);
             e.dataTransfer.dropEffect = 'move';
             e.dataTransfer.effectAllowed = 'move';
             e.dataTransfer.setData('move_id', id);
         },
         remove_element(id) {
             console.log(`Removing ${id}`);
             let args = {
                 session_id: this.bookbuilder.session_id,
                 action: "remove",
                 remove_id: id,
             };
             axios.post('/collector/api/bookbuilder', args)
                  .then(res => {
                      console.log(res.data)
                      this.bookbuilder.add_text(res.data);
                  });
         },
         refresh_list() {
             let args = {
                 session_id: this.bookbuilder.session_id,
                 action: "list",
             };
             axios.post('/collector/api/bookbuilder', args)
                  .then(res => {
                      console.log(res.data)
                      this.bookbuilder.add_text(res.data);
                  });
         },
         download_url() {
             if (this.bookbuilder.job_produced) {
                 return '/collector/api/bookbuilder/' + this.bookbuilder.session_id;
             }
         },
         build() {
             let args = {
                 session_id: this.bookbuilder.session_id,
                 action: "build",
             };
             axios.post('/collector/api/bookbuilder', args)
                  .then(res => {
                      console.log(res.data)
                      if (res.data.job_id) {
                          this.bookbuilder.job_id = res.data.job_id;
                          this.check_job_status();
                      }
                  });
         },
         check_job_status() {
             let jid = this.bookbuilder.job_id;
             if (jid) {
                 let args = {
                     session_id: this.bookbuilder.session_id,
                     action: "check_job",
                     check_job_id: jid,
                 };
                 axios.post('/collector/api/bookbuilder', args)
                      .then(res => {
                          console.log(res.data)
                          status = this.bookbuilder.status = res.data.status
                          console.log("Status is " + status)
                          if (status == 'finished') {
                              console.log("Finished");
                              this.bookbuilder.finish();
                          }
                          else if (status == 'failed') {
                              this.bookbuilder.fail("Job failed");
                          }
                          else {
                              console.log("Repeating it and checking " + jid),
                              setTimeout(() => { this.check_job_status() }, 1000);
                          }
                      });
             }
         }
     },
     mounted() {
         this.bookbuilder.restore();
         this.refresh_list();
     },
 }
</script>
<template>
  <div v-for="text in bookbuilder.text_list" :key="text.sid + text.id">
    <div class="flex my-2">
      <TrashIcon class="h-6 w-6 text-cab-sav-800" @click="remove_element(text.id)" />
      <div @drop="drop_element($event, text.id)"
         @dragover.prevent @dragenter.prevent
         @dragstart="drag_element($event, text.id)"
         draggable="true" class="font-bold cursor-grab">{{ text.id }} {{ text.title }}</div>
    </div>
  </div>
  <div v-if="bookbuilder.can_be_compiled()">
    <button class="btn-accent m-1 px-4 py-1 rounded shadow-lg" @click="build">
      {{ $gettext('Build') }}
    </button>
  </div>
  <div v-if="bookbuilder.status == 'finished'">
    <a :href="download_url()" class="btn-primary m-1 px-4 py-1 rounded shadow-lg">
      {{ $gettext('Download') }}
    </a>
  </div>
  <div v-if="bookbuilder.status == 'failed'">
    <button class="btn-primary m-1 px-4 py-1 rounded shadow-lg">
      {{ $gettext('Failed') }}
    </button>
  </div>
  <div v-if="bookbuilder.status == 'inactive'">
    <button class="btn-accent m-1 px-4 py-1 rounded shadow-lg animate-pulse">
      {{ $gettext('Queued') }}
    </button>
  </div>
  <div v-if="bookbuilder.status == 'active'">
    <button class="btn-accent m-1 px-4 py-1 rounded shadow-lg animate-pulse">
      {{ $gettext('Working') }}
    </button>
  </div>
</template>
