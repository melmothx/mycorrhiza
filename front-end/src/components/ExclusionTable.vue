<script>
 import ExclusionRow from './ExclusionRow.vue'
 import axios from 'axios'
 export default {
     components: { ExclusionRow },
     data() {
         return {
             records: [],
         }
     },
     methods: {
         fetch() {
             const vm = this;
             axios.get('/collector/api/listing/exclusions').then(function(res) {
                 console.log(res.data);
                 vm.records = res.data.exclusions;
             });
         }
     },
     mounted() {
         this.fetch();
     }
     
 }
</script>
<template>
  <div v-if="records.length">
    <h1 class="text-center text-lg font-semibold"><slot></slot></h1>
    <table class="m-1 border">
      <thead class="border">
        <th class="border p-1"></th>
        <th class="border p-1">{{ $gettext('Target') }}</th>
        <th class="border p-1">{{ $gettext('Type') }}</th>
        <th class="border p-1">{{ $gettext('Reason') }}</th>
        <th class="border p-1">{{ $gettext('Date') }}</th>
      </thead>
      <tbody>
        <tr v-for="rec in records" :key="rec.id"
            class="border even:bg-gray-100">
          <ExclusionRow :record="rec" @refetch="fetch" />
        </tr>
      </tbody>
    </table>
  </div>
  <div v-else class="text-center text-lg font-semibold">
    {{ $gettext('Nothing to show!') }}
  </div>
</template>
