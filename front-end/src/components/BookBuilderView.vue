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
             headings: [],
             schemas: [
                 "2up",
                 "duplex2up",
                 "2down",
                 "2side",
                 "4up",
                 "2x4x2",
                 "1x4x2cutfoldbind",
                 "2x4x1",
                 "ea4x4",
                 "1x8x2",
                 "1x1",
             ],
             schema_images: [
                 'schema-1x1-1.png',
                 'schema-1x1-2.png',
                 'schema-1x4x2cutfoldbind-1.png',
                 'schema-1x4x2cutfoldbind-2.png',
                 'schema-1x8x2-1.png',
                 'schema-1x8x2-2.png',
                 'schema-2down-1.png',
                 'schema-2down-2.png',
                 'schema-2down-3.png',
                 'schema-2down-4.png',
                 'schema-2side-1.png',
                 'schema-2side-2.png',
                 'schema-2side-3.png',
                 'schema-2side-4.png',
                 'schema-2up-1.png',
                 'schema-2up-2.png',
                 'schema-2up-3.png',
                 'schema-2up-4.png',
                 'schema-duplex2up-1.png',
                 'schema-duplex2up-2.png',
                 'schema-duplex2up-3.png',
                 'schema-duplex2up-4.png',
                 'schema-2x4x1-1.png',
                 'schema-2x4x1-2.png',
                 'schema-2x4x2-1.png',
                 'schema-2x4x2-2.png',
                 'schema-2x4x2-3.png',
                 'schema-2x4x2-4.png',
                 'schema-4up-1.png',
                 'schema-4up-2.png',
                 'schema-4up-3.png',
                 'schema-4up-4.png',
                 'schema-ea4x4-1.png',
                 'schema-ea4x4-2.png',
                 'schema-ea4x4-3.png',
                 'schema-ea4x4-4.png',
             ],
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
         get_headings() {
             axios.post('/collector/api/bookbuilder', { action: "get_headings" })
                  .then(res => {
                      console.log(res.data);
                      this.headings = res.data.headings;
                  });
         },
         get_schema_images(schema) {
             console.log(`Calling get_schema images for ${schema}`);
             return this.schema_images.filter(img => img.includes('-' + schema + '-'));
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
         this.get_headings();
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
      <div class="flex items-center">
        <div class="mr-2 w-32">
          <label for="bb-papersize">{{ $gettext('Please choose a paper size') }}</label>
        </div>
        <select id="bb-papersize" class="mcrz-select h-8 w-96" v-model="bookbuilder.collection_data.papersize">
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
      </div>
      <div v-if="!bookbuilder.collection_data.papersize" class="my-2">
        <div class="flex items-center">
          <div class="mr-2 w-32">
            <label for="bb-ppw">
              {{ $gettext('Width in mm') }}:
            </label>
          </div>
          <div>
            <input type="number"
                   id="bb-ppw"
                   step="1" min="80" max="500"
                   class="mcrz-input h-8 w-32"
                   v-model="bookbuilder.collection_data.papersize_width">
          </div>
          <div class="w-4"></div>
          <div class="mr-2 w-32">
            <label for="bb-pph">
              {{ $gettext('Height in mm') }}:
            </label>
          </div>
          <div>
            <input type="number" id="bb-pph" class="mcrz-input h-8 w-32"
                   step="1" min="80" max="500"
                   v-model="bookbuilder.collection_data.papersize_height">
          </div>
        </div>
      </div>

      <div>
        <div class="flex items-center my-4">
          <div class="mr-2 w-64">
            <label for="bb-div">
              {{ $gettext('Automatic margins: choose a factor. 9 has the widest margins, 15 the narrowest') }}
            </label>
          </div>
          <div>
            <select id="bb-div" class="mcrz-select h-8 w-32"
                    v-model="bookbuilder.collection_data.division_factor">
              <option value="0">Custom</option>
              <option v-for="div in [9, 10, 11, 12, 13, 14, 15]" :value="div">{{ div }}</option>
            </select>
          </div>
        </div>
        <div v-if="bookbuilder.collection_data.division_factor == 0">
          <div class="flex items-center my-4">
            <div class="mr-2 w-64">
              <label for="bb-aw">
                {{ $gettext('Text block width in mm') }}
              </label>
              <div v-if="bookbuilder.needs_areaset_width()"
                   class="text-sm text-claret-700">
                <small class="font-bold">{{ $gettext('Please set') }}</small>
              </div>
            </div>
            <div>
              <input class="mcrz-input w-32 h-8" id="bb-aw"
                     type="number"
                     step="1" min="30" v-model="bookbuilder.collection_data.areaset_width">
            </div>
          </div>
          <div class="flex items-center my-4">
            <div class="mr-2 w-64">
              <label for="bb-ah">
                {{ $gettext('Text block height in mm') }}
              </label>
              <div v-if="bookbuilder.needs_areaset_height()"
                   class="text-sm text-claret-700">
                <small class="font-bold">{{ $gettext('Please set') }}</small>
              </div>
            </div>
            <div>
              <input class="mcrz-input w-32 h-8" id="bb-ah"
                     type="number"
                     min="30"
                     step="1" v-model="bookbuilder.collection_data.areaset_height">
            </div>
          </div>
          <div class="flex items-center my-4">
            <div class="mr-2 w-64">
              <label for="bb-gom">
                {{ $gettext('Outer margin in mm') }} <br>
                <small class="text-asphalt-700">{{ $gettext('leave blank for default') }}</small>
              </label>
              <div v-if="bookbuilder.needs_geometry_outer_margin()"
                   class="text-sm text-claret-700">
                <small class="font-bold">{{ $gettext('Please set') }}</small>
              </div>
            </div>
            <div>
              <input type="number"
                     class="mcrz-input w-32 h-8" id="bb-gom"
                     min="0"
                     step="1" v-model="bookbuilder.collection_data.geometry_outer_margin">
            </div>
          </div>
          <div class="flex items-center my-4">
            <div class="mr-2 w-64">
              <label for="bb-gtm">
                {{ $gettext('Top margin in mm') }} <br>
                <small class="text-asphalt-700">{{ $gettext('leave blank for default') }}</small>
              </label>
              <div v-if="bookbuilder.needs_geometry_top_margin()"
                   class="text-sm text-claret-700">
                <small class="font-bold">{{ $gettext('Please set') }}</small>
              </div>
            </div>
            <div>
              <input type="number"
                     class="mcrz-input w-32 h-8" id="bb-gtm"
                     min="0"
                     step="1" v-model="bookbuilder.collection_data.geometry_top_margin">
            </div>
          </div>
        </div>
      </div>
      <div>
        <div class="flex items-center my-4">
          <div class="mr-2 w-64">
            <label for="bb-bcor">
              {{ $gettext('Binding correction in mm (additional inner margin)') }}
            </label>
          </div>
          <div>
            <input id="bb-bcor" type="number" step="1" min="0" max="50" class="mcrz-input w-32 h-8"
                   v-model="bookbuilder.collection_data.binding_correction" />
          </div>
        </div>
      </div>
      <div>
        <div class="flex items-center my-4">
          <div class="mr-2 w-64">
            <label>
              <input type="checkbox" value="1" class="mcrz-checkbox"
                     v-model="bookbuilder.collection_data.twoside" />
              <span class="ml-2">
                {{ $gettext('Two side layout') }}
              </span>
            </label>
          </div>
          <div>
          </div>
        </div>
      </div>
      <div v-if="bookbuilder.collection_data.twoside" class="flex items-center my-4">
        <div class="mr-2 w-32">
          <label for="bb-opening">
            {{ $gettext('Page where to start a chapter') }}
          </label>
        </div>
        <div>
          <select id="bb-opening" class="mcrz-select h-8 w-32" v-model="bookbuilder.collection_data.opening">
            <option v-for="opening in ['any', 'right', 'left']" :value="opening">{{ opening }}</option>
          </select>
        </div>
      </div>
      <div class="flex items-center my-4">
        <div class="mr-2 w-32">
          <label for="bb-headings">
            {{ $gettext('Running headings') }}
          </label>
        </div>
        <div>
          <select id="bb-headings" class="mcrz-select h-8 w-full" v-model="bookbuilder.collection_data.headings">
            <option v-for="heading in headings" :value="heading.name" :key="heading.name">{{ heading.desc }}</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="current_tab == 'advanced'" id="bb-layout"
         class="grid sm:grid-cols-[300px_auto] gap-2">
      <div>
        <div class="flex items-center my-4">
          <div class="mr-2 w-32">
            <label for="bb-linespacing">
              {{ $gettext('Line spacing') }}
            </label>
          </div>
          <div>
            <input class="mcrz-input" type="number"
                   id="bb-linespacing"
                   v-model="bookbuilder.collection_data.linespacing"
                   min="1.0" max="2.0" step="0.1" />
          </div>
        </div>
        <div class="flex items-center my-4">
          <div class="mr-2 w-32">
            <label for="bb-parindent">
              {{ $gettext('Paragraph indentation in points (pt)') }}
            </label>
          </div>
          <div>
            <input class="mcrz-input" type="number"
                   id="bb-parindent"
                   v-model="bookbuilder.collection_data.parindent"
                   min="-100" max="100" step="1" />
          </div>
        </div>
        <div class="flex items-center my-4">
          <div class="mr-2 w-32">
            <label for="bb-tex_tolerance">
              {{ $gettext('TeX tolerance') }}
            </label>
          </div>
          <div>
            <input class="mcrz-input" type="number"
                   id="bb-tex_tolerance"
                   v-model="bookbuilder.collection_data.tex_tolerance"
                   min="0" max="10000" step="1" />
          </div>
        </div>
        <div class="flex items-center my-4">
          <div class="mr-2 w-32">
            <label for="bb-tex_emergencystretch">
              {{ $gettext('TeX emergency stretch in pt') }}
            </label>
          </div>
          <div>
            <input class="mcrz-input" type="number"
                   id="bb-tex_emergencystretch"
                   v-model="bookbuilder.collection_data.tex_emergencystretch"
                   min="0" max="10000" step="1" />
          </div>
        </div>
      </div>
      <div class="my-4">
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.notoc" />
            <span class="ml-2">
              {{ $gettext('Never generate a table of content') }}
            </span>
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.nofinalpage" />
            <span class="ml-2">
              {{ $gettext('Never generate the final page with text details') }}
            </span>
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.nocoverpage" />
            <span class="ml-2">
              {{ $gettext('Do not create a cover page and start the text on the first page') }}
            </span>
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.body_only" />
            <span class="ml-2">
              {{ $gettext('Text body only (no title, no final pages)') }}
            </span>
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.impressum" />
            <span class="ml-2">
              {{ $gettext('Place the notes on the back of the first page, impressum-style') }}
            </span>
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.sansfontsections" />
            <span class="ml-2">
              {{ $gettext('Use sans fonts for section titles') }}
            </span>
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.nobold" />
            <span class="ml-2">
              {{ $gettext('Do not use bold fonts') }}
            </span>
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.start_with_empty_page" />
            <span class="ml-2">
              {{ $gettext('Start the document with an empty page') }}
            </span>
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.ignore_cover" />
            <span class="ml-2">
              {{ $gettext('Never display the cover image') }}
            </span>
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.continuefootnotes" />
            <span class="ml-2">
              {{ $gettext('Continuous footnote numbering across the whole document') }}
            </span>
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.centerchapter" />
            <span class="ml-2">
              {{ $gettext('Center chapter titles') }}
            </span>
          </label>
        </div>
        <div>
          <label>
            <input type="checkbox" value="1" class="mcrz-checkbox"
                   v-model="bookbuilder.collection_data.centersection" />
            <span class="ml-2">
              {{ $gettext('Center all section titles') }}
            </span>
          </label>
        </div>
      </div>
    </div>
    <div v-if="current_tab == 'fonts'" id ="bb-fonts">
      <div class="flex items-center my-4">
        <label class="w-32" for="mainfont">{{ $gettext('Main Font')  }}</label>
        <div class="flex-grow">
          <select id="mainfont" class="mcrz-select h-8 w-full" v-model="bookbuilder.collection_data.mainfont">
            <option v-for="font in fonts" :value="font.name">{{ font.desc }}</option>
          </select>
        </div>
      </div>
      <div class="flex items-center my-4">
        <label class="w-32" for="monofont">{{ $gettext('Mono Font')  }}</label>
        <div class="flex-grow">
          <select id="monofont" class="mcrz-select h-8 w-full" v-model="bookbuilder.collection_data.monofont">
            <option v-for="font in fonts.filter(f => f.type == 'mono')" :value="font.name">{{ font.desc }}</option>
          </select>
        </div>
      </div>
      <div class="flex items-center my-4" v-if="bookbuilder.needs_sans_font()">
        <label class="w-32" for="sansfont">{{ $gettext('Sans Font') }}</label>
        <div class="flex-grow">
          <select id="sansfont" class="mcrz-select h-8 w-full" v-model="bookbuilder.collection_data.sansfont">
            <option v-for="font in fonts" :value="font.name">{{ font.desc }}</option>
          </select>
        </div>
      </div>
      <div class="flex items-center my-4">
        <label class="w-32" for="fontsize">{{ $gettext('Font Size') }}</label>
        <div class="flex-grow">
          <select id="fontsize" class="mcrz-select h-8 w-full" v-model="bookbuilder.collection_data.fontsize">
            <option v-for="fs in [9, 10, 11, 12, 13, 14]" :value="fs">{{ fs }}pt</option>
          </select>
        </div>
      </div>
    </div>
    <div v-if="current_tab == 'imposition'" id="bb-imposition">
      <div class="flex items-center my-4">
        <label class="w-32" for="imposition_schema">
          {{ $gettext('Imposition Schema') }}
        </label>
        <select id="imposition_schema"
                class="mcrz-select h-8"
                v-model="bookbuilder.collection_data.imposition_schema">
          <option value="">{{ $gettext('None') }}</option>
          <option v-for="schema in schemas" :value="schema">{{ schema }}</option>
        </select>
      </div>
      <div class="flex">
        <img v-for="image in get_schema_images(bookbuilder.collection_data.imposition_schema)"
             :src="'/schemas/' + image"
             class="w-full m-2 max-w-64"
        >
      </div>
      <div v-if="bookbuilder.collection_data.imposition_schema == '2up'" class="m-2">
        <p>
          {{ $gettext('Pages are reordered, in one or more groups (signatures), then folded in half. If you have more signatures, you will have to bound them together like a book. With this option, you may want to decide the size of the signatures. This can be a fixed value (4,8,16, etc.), the whole book in a single signature, or an optimized size to reduce the number of blank pages.') }}
        </p>
      </div>
      <div v-if="bookbuilder.collection_data.imposition_schema == 'duplex2up'" class="m-2">
        <p>
          {{ $gettext('Same as 2UP, but for duplex printers') }}
        </p>
      </div>
      <div v-if="bookbuilder.collection_data.imposition_schema == '2down'" class="m-2">
        <p>
          {{ $gettext('Same as 2UP, but the pages are rotated by 90 degrees counter-clockwise, binding on the top edge.') }}
        </p>
      </div>
      <div v-if="bookbuilder.collection_data.imposition_schema == '2side'" class="m-2">
        <p>
          {{ $gettext('Pairs of consecutives pages are put on the same sheet side by side.') }}
        </p>
      </div>
      <div v-if="bookbuilder.needs_signature_2up()" class="m-2 flex items-center">
        <div class="mr-2 w-32">
          <label for="bb-signature-2up">
            {{ $gettext('Please select the signature size') }}
          </label>
        </div>
        <select class="mcrz-select h-8"
                id="bb-signature-2up" v-model="bookbuilder.collection_data.signature_2up">
          <option value="0">{{ $gettext('The whole book in as single signature') }}</option>
          <option value="40-80">{{ $gettext('Use optimized signatures with 40-80 pages each') }}</option>
          <option v-for="signature in [ 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80 ]"
                  :value="signature">
            {{ signature }}
          </option>
        </select>
      </div>
      <div v-if="bookbuilder.collection_data.imposition_schema == '4up'" class="m-2">
        <p>
          {{ $gettext('Exactly like 2up, but the sheets are meant to be cut horizontally first and then stacked on each other. This way you can print, for example, A6 booklets on A4.') }}
        </p>
      </div>
      <div v-if="bookbuilder.needs_signature_4up()" class="m-2 flex items-center">
        <div class="mr-2 w-32">
          <label for="bb-signature-4up">
            {{ $gettext('Please select the signature size') }}
          </label>
        </div>
        <select class="mcrz-select h-8"
                id="bb-signature-4up" v-model="bookbuilder.collection_data.signature_4up">
          <option value="0">{{ $gettext('The whole book in as single signature') }}</option>
          <option value="40-80">{{ $gettext('Use optimized signatures with 40-80 pages each') }}</option>
          <option v-for="signature in [ 8, 16, 24, 32, 40, 48, 56, 64, 72, 80 ]"
                  :value="signature">
            {{ signature }}
          </option>
        </select>
      </div>
      <div v-if="bookbuilder.collection_data.imposition_schema == '2x4x1'" class="m-2">
        <p>
          {{ $gettext('Blocks of 8 pages to be folded twice and then bound together.') }}
        </p>
      </div>
      <div v-if="bookbuilder.collection_data.imposition_schema == '2x4x2'" class="m-2">
        <p>
          {{ $gettext('Blocks of 16 pages to be folded twice and then bound together.') }}
        </p>
      </div>
      <div v-if="bookbuilder.collection_data.imposition_schema == '1x4x2cutfoldbind'" class="m-2">
        <p>
          {{ $gettext('Fixed signatures of 8 pages, to be cut horizontally, folded individually, and bound together.') }}
        </p>
      </div>
      <div v-if="bookbuilder.collection_data.imposition_schema == '1x8x2'" class="m-2">
        <p>
          {{ $gettext('Fixed 16 pages signatures on a single sheet, with triple folding.') }}
          <a target="_blank" href="https://metacpan.org/pod/PDF::Imposition::Schema1x8x2">
            {{ $gettext('See here for more details') }}
          </a>
        </p>
      </div>
      <div v-if="bookbuilder.collection_data.imposition_schema == 'ea4x4'" class="m-2">
        <p>
          {{ $gettext('Fixed 16 pages signatures on 2 sheets, with double individual folding.') }}
          <a target="_blank" href="https://metacpan.org/pod/PDF::Imposition::Schemaea4x4">
            {{ $gettext('See here for more details') }}
          </a>
        </p>
      </div>
      <div v-if="bookbuilder.collection_data.imposition_schema == '1x1'" class="m-2">
        <p>
          {{ $gettext('One page per sheet. This is useful only if you want to add the cropmarks') }}
        </p>
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
{{ bookbuilder.api_collection_data() }}
    </pre>
  </div>
</template>
