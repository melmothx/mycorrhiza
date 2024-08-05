<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import { Listbox, ListboxButton, ListboxOptions, ListboxOption, } from '@headlessui/vue'
 import { ChevronUpDownIcon,  } from '@heroicons/vue/24/solid'
 export default {
     components: {
         Listbox, ListboxButton, ListboxOptions, ListboxOption,
         ChevronUpDownIcon,
     },
     props: [ 'library_id' ],
     data() {
         return {
             "spreadsheet" : null,
             "spreadsheet_name" : null,
             "comment": "",
             "site_options": [],
             "site": {},
             "replace_all": false,
             "error": null,
             "success": null,
             "sample": [],
         }
     },
     methods: {
         fetch() {
             axios.get('/collector/api/spreadsheet/' + this.library_id)
                  .then(res => {
                      if (res.data.sites && res.data.sites.length) {
                          this.site_options = res.data.sites;
                          this.site = this.site_options[0];
                      }
                  })
                  .catch(error => {
                      this.error = error;
                  });
         },
         load_file(event) {
             this.spreadsheet = event.target.files[0];
             this.spreadsheet_name = this.spreadsheet.name;
         },
         upload () {
             console.log("Uploading");
             let form_data = new FormData();
             form_data.append('spreadsheet', this.spreadsheet);
             form_data.append('site_id', this.site.id);
             form_data.append('comment', this.comment);
             form_data.append('replace_all', this.replace_all ? "1" : "");
             console.log(form_data);
             this.error = null;
             this.success = null;
             axios.post('/collector/api/spreadsheet/' + this.library_id,
                        form_data, {
                            headers: {
                                'Content-Type': 'multipart/form-data'
                            }
                        })
                  .then(res => {
                      console.log(res.data);
                      this.error = res.data.error;
                      this.success = res.data.success;
                      this.sample = res.data.sample;
                      this.spreadsheet_id = res.data.uploaded;
                  })
                  .catch(err => {
                      this.error = err;
                  });
         },
         confirm_process() {
             this.sample = [];
             this.spreadsheet = null;
             this.spreadsheet_name = null;
             axios.post('/collector/api/spreadsheet/process/' + this.spreadsheet_id)
                  .then(res => {
                      console.log(res.data)
                      this.spreadsheet_id = null;
                      this.error = res.data.error;
                      this.success = res.data.success;
                  })
                  .catch(err => {
                      this.error = err;
                  });
         },
         cancel_process() {
             this.error = null;
             this.success = null;
             this.sample = [];
             this.spreadsheet_id = null;
             this.spreadsheet = null;
             this.spreadsheet_name = null;
         },
     },
     mounted() {
         this.fetch();
     },
 }
</script>
<template>
  <div v-if="site_options.length && !sample.length">
    <form @submit.prevent="upload">
      <h1 class="font-bold text-xl mb-2">{{ $gettext('Upload a CSV') }}</h1>
      <div v-if="error" class="py-2 text-claret-900 font-bold">
        {{ $gettext(error) }}
      </div>
      <div v-if="success" class="py-2 text-spectra-800 font-bold">
        {{ $gettext(success) }}
      </div>
      <div class="mb-4">
        <div>
          <label for="csv-upload-file" class="btn-accent p-1 mr-3 cursor-pointer">
            <template v-if="spreadsheet_name">
              {{ $gettext('Choose another file') }}
            </template>
            <template v-else>
              {{ $gettext('Choose file') }}
            </template>
          </label>
        </div>
        <div class="w-0 h-0">
          <input id="csv-upload-file" class="w-0" type="file" @change="load_file($event)" required>
        </div>
        <div>
          <span class="font-bold">{{spreadsheet_name}}</span>
        </div>
      </div>
      <div v-if="site_options.length > 1">
        <Listbox v-model="site">
          <div class="relative m-0 mt-2">
            <ListboxButton class="mcrz-listbox-button"
                           v-slot="{ open }">
              <span class="block truncate">{{ $gettext('Source:') }} {{ site.title }}</span>
              <span class="mcrz-select-chevron-container">
                <ChevronUpDownIcon
                    class="h-5 w-5 text-gray-400"
                    aria-hidden="true"
                />
              </span>
            </ListboxButton>
            <transition
                enter-active-class="transition duration-100 ease-out"
                enter-from-class="transform scale-95 opacity-0"
                enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-75 ease-in"
                leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0">
              <ListboxOptions class="mcrz-listbox-options">
                <ListboxOption v-for="site in site_options"
                               :value="site" :key="site.id"
                               class="cursor-pointer hover:text-spectra-800 py-1"
                >{{ site.title }}</ListboxOption>
              </ListboxOptions>
            </transition>
          </div>
        </Listbox>
      </div>
      <div>
        <label for="csv-comment">Comment</label>
      </div>
      <div class="flex">
        <textarea id="csv-comment" class="mcrz-textarea" v-model="comment"></textarea>
      </div>
      <label>
        <input type="checkbox" class="mcrz-checkbox" v-model="replace_all">
        <span class="ml-1">
          {{ $gettext('Replace all records') }}
        </span>
      </label>
      <div class="mt-2">
        <button class="btn-primary p-1" type="submit">
          {{ $gettext('Upload File') }}
        </button>
      </div>
    </form>
  </div>
  <div v-if="sample.length">
    <table>
      <thead>
        <tr>
          <th>{{ $gettext('Column Name') }}</th>
          <th>{{ $gettext('Value') }}</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="col in sample">
          <tr v-if="col.name">
            <td>
              {{ col.name }}
            </td>
            <td>
              {{ col.value }}
            </td>
          </tr>
        </template>
      </tbody>
    </table>
    <button v-if="spreadsheet_id"
            @click="confirm_process"
            class="btn-primary p-1"
            type="button">
      {{ $gettext('Process File') }}
    </button>
    <button v-if="spreadsheet_id"
            @click="cancel_process"
            class="btn-primary p-1"
            type="button">
      {{ $gettext('Cancel') }}
    </button>

  </div>
</template>
