<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import { TrashIcon, ChevronUpDownIcon } from '@heroicons/vue/24/solid'
 export default {
     components: { TrashIcon, ChevronUpDownIcon },
     props: [
         'listing_url',
         'removal_url',
         'table_title',
     ],
     data() {
         return {
             all_records: [],
             records: [],
             fields: [],
             search_string: "",
             sort_field: "",
             sort_direction: "desc",
             working: false,
         }
     },
     methods: {
         fetch() {
             const vm = this;
             // these are the exclusion I set
             axios.get(this.listing_url).then(function(res) {
                 vm.fields = res.data.fields;
                 vm.all_records = res.data.records;
                 vm.records = vm.all_records.filter(() => true);
             });
         },
         remove(id) {
             const vm = this;
             if (id) {
                 console.log("Removing " + id)
                 vm.working = true;
                 axios.post(this.removal_url, { id: id })
                      .then(function(res) {
                            console.log(res.data);
                            vm.fetch();
                          vm.working = false;
                      })
                      .catch(function(error) {
                          vm.working = false;
                          console.log(error);
                      });
             }
         },
         sort_records_asc(field) {
             this.records.sort(function(a, b) {
                 if (a[field] == b[field]) {
                     return 0;
                 }
                 else if (a[field] < b[field]) {
                     return -1
                 }
                 else {
                     return 1
                 }
             });
         },
         sort_records_desc(field) {
             this.records.sort(function(a, b) {
                 if (a[field] == b[field]) {
                     return 0;
                 }
                 else if (a[field] < b[field]) {
                     return 1
                 }
                 else {
                     return -1
                 }
             });
         },
         sort_rows(field) {
             console.log(`Sorting by ${field}`);
             if (this.sort_field && this.sort_field == field) {
                 if (this.sort_direction == 'desc') {
                     this.sort_direction = 'asc';
                     this.sort_records_asc(field);
                 }
                 else {
                     this.sort_direction = 'desc';
                     this.sort_records_desc(field);
                 }
             }
             else {
                 this.sort_direction = 'asc';
                 this.sort_records_asc(field);
             }
             this.sort_field = field;
         },
         filter_by_search() {
             let sf = this.fields.map((f) => f.name);
             if (this.search_string) {
                 let search = this.search_string.toLowerCase();
                 this.records = this.all_records.filter((el) => {
                     for (const f of sf) {
                         if (el[f] && el[f].toString().toLowerCase().includes(search)) {
                             console.log(el[f])
                             return true;
                         }
                     }
                 });
             }
             else {
                 this.records = this.all_records.filter(() => true);
             }
         },
     },
     mounted() {
         this.fetch();
     }
 }
 /*
    $gettext('ID')
    $gettext('Title')
    $gettext('Subtitle')
 */
</script>
<template>
  <div v-if="all_records.length > 0">
    <div v-if="table_title">
      <h1 class="font-bold text-xl mb-2">{{ table_title }}</h1>
    </div>
    <div v-if="working" class="m-2 text-center">
      <span class="animate-ping rounded-full text-claret-900 p-2">{{ $gettext('Working') }}</span>
    </div>
    <div class="flex mb-2">
      <input class="mcrz-input"
             v-model="search_string" @input="filter_by_search" placeholder="Search table here">
    </div>
    <table>
      <thead>
        <tr class="text-spectra-900 text-left bg-perl-bush-50">
          <template v-for="f in fields" :key="f.name">
            <th class="pl-1 pr-4 cursor-pointer"
                :title="$gettext('Click to sort')"
                @click="sort_rows(f.name)">
              <div class="flex whitespace-nowrap">
                <span class="flex-grow">
                  {{ $gettext(f.label) }}
                </span>
                <span>
                  <ChevronUpDownIcon class="w-6 h-6" />
                </span>
              </div>
            </th>
          </template>
          <th v-if="records.length" class="pl-1 pr-4">
            Remove
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="record in records" :id="record.id" class="bg-perl-bush-50 odd:bg-perl-bush-100">
          <td class="p-1" v-for="f in fields" :key="f.name">
            <template v-if="f.link == 'entry'">
              <button @click="$router.push({ name: 'entry', params: { id: record[f.name] } })">
                {{ record[f.name] }}
              </button>
            </template>
            <template v-else>
              {{ record[f.name] }}
            </template>
          </td>
          <td class="text-center text-claret-800 hover:text-claret-600">
            <button @click="remove(record.id)">
              <TrashIcon class="h-4 w-4"/>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div v-else>
    <em>{{ $gettext('Nothing to show') }}</em>
  </div>
</template>
