<script>
 import axios from 'axios'
 import { bookbuilder } from '../stores/bookbuilder.js'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import { TrashIcon,
          Cog8ToothIcon,
          ArrowPathIcon,
          BookOpenIcon,
 } from '@heroicons/vue/24/solid'
 export default {
     components: {
         TrashIcon,
         Cog8ToothIcon,
         ArrowPathIcon,
         BookOpenIcon,
      },
     data() {
         return {
             bookbuilder,
             current_tab: "overview",
             fonts: [],
         }
     },
     methods: {
         set_tab(tab) {
             this.bookbuilder.save();
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
         get_fonts() {
             axios.post('/collector/api/bookbuilder', { action: "get_fonts" })
                  .then(res => {
                      console.log(res.data);
                      this.fonts = res.data.fonts;
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
             this.bookbuilder.save();
             const args = {
                 session_id: this.bookbuilder.session_id,
                 collection_data: this.bookbuilder.api_collection_data(),
                 action: "build",
             };
             console.log(args);
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
         this.get_fonts();
         this.bookbuilder.restore();
         this.refresh_list();
     },
 }
</script>
<template>
  <div class="font-medium text-center text-gray-500 mb-8">
    <ul class="flex flex-wrap">
      <li>
        <a href="#" @click="set_tab('overview')" :class="current_tab == 'overview' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          {{ $gettext('Overview') }}
        </a>
      </li>
      <li>
        <a href="#" @click="set_tab('layout')" :class="current_tab == 'layout' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          {{ $gettext('Layout') }}
        </a>
      </li>
      <li>
        <a href="#" @click="set_tab('fonts')" :class="current_tab == 'fonts' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          {{ $gettext('Fonts') }}
        </a>
      </li>
      <li>
        <a href="#" @click="set_tab('imposition')" :class="current_tab == 'imposition' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          {{ $gettext('Imposition') }}
        </a>
      </li>
      <li>
        <a href="#" @click="set_tab('advanced')" :class="current_tab == 'advanced' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          {{ $gettext('Advanced') }}
        </a>
      </li>
    </ul>
  </div>
  <div id="bb-tabs">
    <div v-if="current_tab == 'layout'" id="bb-layout">
      <select class="mcrz-select" v-model="bookbuilder.collection_data.papersize">
        <option value="generic">Generic (fits in A4 and Letter)</option>
        <option value="a3">A3</option>
        <option value="a4">A4</option>
        <option value="a5">A5</option>
        <option value="a6">A6</option>
        <option value="88mm:115mm">6" E-reader</option>
        <option value="b3">B3</option>
        <option value="b4">B4</option>
        <option value="b5">B5</option>
        <option value="b6">B6</option>
        <option value="letter">Letter paper</option>
        <option value="5.5in:8.5in">Half Letter paper</option>
        <option value="4.25in:5.5in">Quarter Letter paper</option>
        <option value="">Custom</option>
      </select>
      <div v-if="!bookbuilder.collection_data.papersize">
        <input type="number" step="1" min="80" max="500" class="mcrz-input" v-model="bookbuilder.collection_data.papersize_width">
        x
        <input type="number" step="1" min="80" max="500" class="mcrz-input" v-model="bookbuilder.collection_data.papersize_height">
      </div>
    </div>
    <div v-if="current_tab == 'fonts'" id ="bb-fonts">
      <div>
        <label for="mainfont">{{ $gettext('Main Font')  }}</label>
        <div>
          <select id="mainfont" class="mcrz-select" v-model="bookbuilder.collection_data.mainfont">
            <option v-for="font in fonts" :value="font.name">{{ font.desc }}</option>
          </select>
        </div>
      </div>
      <div>
        <label for="monofont">{{ $gettext('Mono Font')  }}</label>
        <div>
          <select id="monofont" class="mcrz-select" v-model="bookbuilder.collection_data.monofont">
            <option v-for="font in fonts.filter(f => f.type == 'mono')" :value="font.name">{{ font.desc }}</option>
          </select>
        </div>
      </div>
      <div v-if="bookbuilder.needs_sans_font()">
        <label for="sansfont">{{ $gettext('Sans Font') }}</label>
        <div>
          <select id="sansfont" class="mcrz-select" v-model="bookbuilder.collection_data.sansfont">
            <option v-for="font in fonts" :value="font.name">{{ font.desc }}</option>
          </select>
        </div>
      </div>
    </div>
    <div v-if="current_tab == 'overview'" id="bb-overview">
      <div class="my-4" v-if="bookbuilder.needs_virtual_header()">
        <div>
          <div clas="flex">
            <input id="library-collection-title" class="w-full mcrz-input" :placeholder="$gettext('Title')"
                   v-model="bookbuilder.collection_data.title" />
          </div>
          <div clas="flex">
            <input id="library-collection-subtitle" class="w-full mcrz-input" :placeholder="$gettext('Subtitle')"
                   v-model="bookbuilder.collection_data.subtitle" />
          </div>
          <div clas="flex">
            <input id="library-collection-author" class="w-full mcrz-input" :placeholder="$gettext('Author')"
                   v-model="bookbuilder.collection_data.author" />
          </div>
          <div clas="flex">
            <input id="library-collection-date" class="w-full mcrz-input" :placeholder="$gettext('Date')"
                   v-model="bookbuilder.collection_data.date" />
          </div>
          <div clas="flex">
            <input id="library-collection-notes" class="w-full mcrz-input" :placeholder="$gettext('Notes')"
                   v-model="bookbuilder.collection_data.notes" />
          </div>
          <div clas="flex">
            <input id="library-collection-source" class="w-full mcrz-input" :placeholder="$gettext('Source')"
                   v-model="bookbuilder.collection_data.source" />
          </div>
        </div>
      </div>
      <div v-for="text in bookbuilder.text_list" :key="text.sid + text.id">
        <div class="flex my-3">
          <router-link :to="{name: 'entry', params: { id: text.attributes.entry_id } }">
            <BookOpenIcon class="h-6 w-6 mr-3 text-spectra-700" />
          </router-link>
          <div @drop="drop_element($event, text.id)"
         @dragover.prevent @dragenter.prevent
         @dragstart="drag_element($event, text.id)"
         draggable="true" class="font-bold cursor-grab">{{ text.attributes.title }}</div>
          <TrashIcon class="ml-3 h-6 w-6 text-cab-sav-800 cursor-pointer" @click="remove_element(text.id)" />
        </div>
      </div>
    </div>
  </div>
  <div id="bb-action" class="mt-8 flex">
    <div v-if="bookbuilder.can_be_compiled()">
      <button class="btn-accent m-1 px-4 py-1 rounded shadow-lg" @click="build">
        {{ $gettext('Build') }}
      </button>
    </div>
    <div v-if="bookbuilder.session_id && !bookbuilder.status">
      <button class="btn-accent m-1 px-4 py-1 rounded shadow-lg" @click="bookbuilder.reset">
        {{ $gettext('Reset') }}
      </button>
    </div>
    <a v-if="bookbuilder.status == 'finished'" :href="download_url()">
      <div class="btn-accent m-1 px-4 py-1 rounded shadow-lg">
        {{ $gettext('Download') }}
      </div>
    </a>
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
  <div class="mt-10">
    <pre class="text-sm">
{{ bookbuilder.collection_data }}
    </pre>
  </div>
</template>
