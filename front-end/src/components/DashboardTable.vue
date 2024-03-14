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
             records: [],
             fields: [],
         }
     },
     methods: {
         fetch() {
             const vm = this;
             const listing_type = this.listing_type
             // these are the exclusion I set
             axios.get('/collector/api/listing/' + listing_type).then(function(res) {
                 console.log(res.data);
                 vm.fields = res.data.fields;
                 vm.records = res.data.records;
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
  <h1><slot></slot></h1>
  <table>
    <thead>
      <tr>
        <th v-for="f in fields" :key="f.name">
          {{ f.label }}
        </th>
        <th>
          Remove
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="record in records" :id="record.id">
        <td v-for="f in fields" :key="f.name">
          {{ record[f.name] }}
        </td>
        <td>
          <button @click="remove(record.id)">Remove</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
