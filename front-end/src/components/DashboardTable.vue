<script>
 import axios from 'axios'
 import { TrashIcon, BarsArrowDownIcon, BarsArrowUpIcon } from '@heroicons/vue/24/solid'
 export default {
     components: { TrashIcon, BarsArrowDownIcon, BarsArrowUpIcon },
     props: [
         'listing_type',
     ],
     data() {
         return {
             all_records: [],
             records: [],
             fields: [],
             search_string: "",
         }
     },
     methods: {
         fetch() {
             const vm = this;
             const listing_type = this.listing_type
             // these are the exclusion I set
             axios.get('/collector/api/listing/' + listing_type).then(function(res) {
                 vm.fields = res.data.fields;
                 vm.all_records = res.data.records;
                 vm.records = vm.all_records.filter(() => true);
             });
         },
         remove(id) {
             const vm = this;
             if (id) {
                 console.log("Removing " + id)
                 axios.post('/collector/api/revert/' + vm.listing_type,
                            {
                                id: id,
                            },
                            {
                                "xsrfCookieName": "csrftoken",
                                "xsrfHeaderName": "X-CSRFToken",
                            })
                        .then(function(res) {
                            console.log(res.data);
                            vm.fetch();
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
  <div class="flex">
    <div class="flex-grow">
      <h1 class="capitalize bold text-lg text-center font-bold mb-8"><slot></slot></h1>
    </div>
    <div>
      <button class="btn-primary rounded-br-3xl h-8 pr-10 pl-4 pr-10"
              type="button" @click="$router.go(-1)">{{ $gettext('Back') }}</button>
    </div>
  </div>
  <div class="flex mb-2">
    <input class="mcrz-input"
           v-model="search_string" @input="filter_by_search" placeholder="Search table here">
  </div>
  <table>
    <thead>
      <tr class="text-spectra-900 text-left bg-perl-bush-50">
        <th v-for="f in fields" :key="f.name" class="pl-1 pr-4">
          {{ f.label }}
          <BarsArrowUpIcon class="cursor-pointer w-4 inline" @click="sort_records_asc(f.name)" />
          <BarsArrowDownIcon class="cursor-pointer w-4 inline" @click="sort_records_desc(f.name)" />
        </th>
        <th class="pl-1 pr-4">
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
</template>
