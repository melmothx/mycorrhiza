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
             "comment": "",
             "site_options": [],
             "site": {},
             "csv_type_options": [],
             "csv_type": {},
             "replace_all": false,
         }
     },
     methods: {
         load_file(event) {
             this.spreadsheet = event.target.files[0];
             console.log(this.spreadsheet);
         },
         upload () {
             console.log([this.spreadsheet,
                          this.comment,
                          this
             ]);
         },
     },
     mounted() {
     }
 }
</script>
<template>
  <div class="mt-4">
    <form @submit.prevent="upload">
      <h1 class="font-bold text-xl mb-6">{{ $gettext('Upload a CSV') }}</h1>
      <label for="csv-upload-file">
        Upload
      </label>
      <input id="csv-upload-file" class="w-0" type="file" @change="load_file($event)" required>
      <div class="flex">
        <textarea class="mcrz-textarea" v-model="comment"></textarea>
      </div>
      <label>
        <input type="checkbox" class="mcrz-checkbox" v-model="replace_all">
        <span class="ml-1">
          {{ $gettext('Replace all records') }}
        </span>
      </label>

      <Listbox v-model="site">
        <div class="relative m-0">
          <ListboxButton class="mcrz-listbox-button"
                         v-slot="{ open }">
            <span class="block truncate">{{ site.name }}</span>
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
              >{{ $gettext(site.name) }}</ListboxOption>
            </ListboxOptions>
          </transition>
        </div>
      </Listbox>

      <Listbox v-model="csv_type">
        <div class="relative m-0">
          <ListboxButton class="mcrz-listbox-button"
                         v-slot="{ open }">
            <span class="block truncate">{{ csv_type.name }}</span>
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
              >{{ $gettext(ct.name) }}</ListboxOption>
            </ListboxOptions>
          </transition>
        </div>
      </Listbox>
      <button class="btn-primary p-1" type="submit">
        {{ $gettext('Upload File') }}
      </button>
    </form>
  </div>
</template>
