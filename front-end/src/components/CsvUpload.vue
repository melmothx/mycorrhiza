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
             "csv_type_options": [],
             "csv_type": {},
             "replace_all": false,
             "error": null,
             "success": null,
         }
     },
     methods: {
         fetch() {
             axios.get('/collector/api/spreadsheet/' + this.library_id)
                  .then(res => {
                      if (res.data.sites && res.data.sites.length) {
                          this.site_options = res.data.sites;
                          this.site = this.site_options[0];
                          this.csv_type_options = res.data.csv_types;
                          this.csv_type = this.csv_type_options[0];
                      }
                  })
                  .catch(error => {
                      this.error = error;
                  });
         },
         load_file(event) {
             this.spreadsheet = event.target.files[0];
             console.log(this.spreadsheet);
             this.spreadsheet_name = this.spreadsheet.name;
         },
         upload () {
             console.log("Uploading");
             let form_data = new FormData();
             form_data.append('spreadsheet', this.spreadsheet);
             form_data.append('site_id', this.site.id);
             form_data.append('csv_type', this.csv_type.id);
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
                  })
                  .catch(err => {
                      this.error = err;
                  });
         },
     },
     mounted() {
         this.fetch();
     },
 }
</script>
<template>
  <div v-if="error" class="py-2 text-claret-900 font-bold">
    {{ $gettext(error) }}
  </div>
  <div v-if="success" class="py-2 text-spectra-800 font-bold">
    {{ $gettext(success) }}
  </div>
  <div class="mt-4" v-if="site_options.length">
    <form @submit.prevent="upload">
      <h1 class="font-bold text-xl mb-6">{{ $gettext('Upload a CSV') }}</h1>
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
      <Listbox v-model="csv_type">
        <div class="relative m-0 mt-2">
          <ListboxButton class="mcrz-listbox-button"
                         v-slot="{ open }">
            <span class="block truncate">{{ $gettext('CSV type:') }} {{ csv_type.title }}</span>
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
              <ListboxOption v-for="ct in csv_type_options"
                             :value="ct" :key="ct.id"
                             class="cursor-pointer hover:text-spectra-800 py-1"
              >{{ $gettext(ct.title) }}</ListboxOption>
            </ListboxOptions>
          </transition>
        </div>
      </Listbox>
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
</template>
