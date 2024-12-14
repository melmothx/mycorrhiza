<script>
 import axios from 'axios'
 import { bookbuilder } from '../stores/bookbuilder.js'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import { TrashIcon, Cog8ToothIcon, ArrowPathIcon } from '@heroicons/vue/24/solid'
 export default {
     components: {
         TrashIcon,
         Cog8ToothIcon,
         ArrowPathIcon,
     },
     data() {
         return {
             bookbuilder,
             current_tab: "general",
         }
     },
     methods: {
         set_tab(tab) {
             this.current_tab = tab;
         },
         drop_element(event, id) {
             const move_id = event.dataTransfer.getData('move_id');
             console.log(`Dropping ${move_id} into ${id}`);
             const args = {
                 session_id: this.bookbuilder.session_id,
                 action: "reorder",
                 move_id: move_id,
                 to_id: id,
             };
             axios.post('/collector/api/bookbuilder', args)
                  .then(res => {
                      console.log(res.data)
                      this.bookbuilder.add_text(res.data);
                  });
         },
         drag_element(e, id) {
             console.log(`Dragging ${id}`);
             e.dataTransfer.dropEffect = 'move';
             e.dataTransfer.effectAllowed = 'move';
             e.dataTransfer.setData('move_id', id);
         },
         remove_element(id) {
             console.log(`Removing ${id}`);
             const args = {
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
             const args = {
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
             const args = {
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
                 const args = {
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
  <div class="font-medium text-center text-gray-500 mb-8">
    <ul class="flex flex-wrap">
      <li>
        <a href="#" @click="set_tab('general')" :class="current_tab == 'general' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          General
        </a>
      </li>
      <li>
        <a href="#" @click="set_tab('layout')" :class="current_tab == 'layout' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          Layout
        </a>
      </li>
      <li>
        <a href="#" @click="set_tab('fonts')" :class="current_tab == 'fonts' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          Fonts
        </a>
      </li>
      <li>
        <a href="#" @click="set_tab('imposition')" :class="current_tab == 'imposition' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          Imposition
        </a>
      </li>
      <li>
        <a href="#" @click="set_tab('advanced')" :class="current_tab == 'advanced' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          Advanced
        </a>
      </li>
    </ul>
  </div>
  <div id="bb-tabs">
    <div v-if="current_tab == 'general'" id="bb-general">
      <div v-for="text in bookbuilder.text_list" :key="text.sid + text.id">
        <div class="flex my-2">
          <TrashIcon class="h-6 w-6 text-cab-sav-800" @click="remove_element(text.id)" />
          <div @drop="drop_element($event, text.id)"
         @dragover.prevent @dragenter.prevent
         @dragstart="drag_element($event, text.id)"
         draggable="true" class="font-bold cursor-grab">{{ text.id }} {{ text.title }}</div>
        </div>
      </div>
    </div>
  </div>
  <div id="bb-action" class="text-center mt-8">
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
      <button class="btn-accent m-1 px-4 py-1 rounded shadow-lg">
        <span class="flex items-center">
          <ArrowPathIcon class="h-4 w-4 mr-1 animate-spin" />
          {{ $gettext('Queued') }}
        </span>
      </button>
    </div>
    <div v-if="bookbuilder.status == 'active'">
      <button type="button" class="btn-accent m-1 px-4 py-1 rounded shadow-lg">
        <span class="flex items-center">
          <Cog8ToothIcon class="h-4 w-4 mr-1 animate-spin" />
          {{ $gettext('Working') }}
        </span>
      </button>
    </div>
  </div>
</template>
