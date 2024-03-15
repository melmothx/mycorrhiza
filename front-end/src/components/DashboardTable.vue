<script>
 import axios from 'axios'
 // import DashboardMergedEntry from './DashboardMergedEntry.vue'
 export default {
     // components: { DashboardMergedEntry },
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
  <h1>
    <slot></slot>
    <button class="font-sans border rounded bg-pink-500 hover:bg-pink-700 text-white font-semibold p-1"
            type="button" @click="$router.go(-1)">{{ $gettext('Back') }}</button>
  </h1>
  <input v-model="search_string" @input="filter_by_search" placeholder="Search table here">
  <table>
    <thead>
      <tr>
        <th v-for="f in fields" :key="f.name">
          {{ f.label }}
          <span class="cursor-pointer" @click="sort_records_asc(f.name)">↓</span>
          <span class="cursor-pointer" @click="sort_records_desc(f.name)">↑</span>
        </th>
        <th>
          Remove
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="record in records" :id="record.id">
        <td v-for="f in fields" :key="f.name">
          <template v-if="f.link == 'entry'">
            <button @click="$router.push({ name: 'entry', params: { id: record[f.name] } })">
              {{ record[f.name] }}
            </button>
          </template>
          <template v-else>
            {{ record[f.name] }}
          </template>
        </td>
        <td>
          <button @click="remove(record.id)">Remove</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
