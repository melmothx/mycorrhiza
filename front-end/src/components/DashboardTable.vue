<script>
 import axios from 'axios'
 export default {
     props: ['listing_type'],
     data() {
         return {
             records: [],
         }
     },
     methods: {
         fetch() {
             const vm = this;
             const listing_type = this.listing_type
             // these are the exclusion I set
             axios.get('/collector/api/listing/' + listing_type).then(function(res) {
                 console.log(res.data);
                 vm.records = res.data[listing_type];
             });
         }
     },
     mounted() {
         this.fetch();
     }
 }
</script>
<template>
  <h1><slot></slot></h1>
  <div v-for="record in records" :id="record.id">
    {{ record.id }}
  </div>
</template>
