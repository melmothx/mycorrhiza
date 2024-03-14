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
                 console.log(res.data.fields);
                 vm.fields = res.data.fields;
                 vm.records = res.data.records;

             });
         }
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
      </tr>
    </thead>
    <tbody>
      <tr v-for="record in records" :id="record.id">
        <td v-for="f in fields" :key="f.name">
          {{ record[f.name] }}
        </td>
      </tr>
    </tbody>
  </table>
</template>
