<script>
 import EntryDetails from './EntryDetails.vue'
 import DataSourceBox from './DataSourceBox.vue'
 import axios from 'axios'
 export default {
     props: [ 'entry_id' ],
     components: { EntryDetails, DataSourceBox },
     data() {
         return {
             record: {},
         }
     },
     methods: {
         fetch_record() {
             const vm = this;
             if (vm.entry_id) {
                 console.log("Fetch " + vm.entry_id);
                 axios.get('/collector/api/entry/' + vm.entry_id)
                      .then(function(res) {
                          vm.record = res.data;
                      });
             }
             else {
                 console.log("Resetting");
                 vm.record = {}
             }
         },
     },
     mounted () {
         this.fetch_record()
     },
     watch: {
         entry_id(new_id, old_id) {
             console.log("Id changed from " + old_id + " to " + new_id);
             this.fetch_record()
         }
     },
 }
</script>
<template>
  <div class="fixed top-0 left-0 right-0 z-50 bg-gradient-to-tr from-perl-bush-100 to-perl-bush-200 h-full overflow-y-auto">
    <div class="m-5 p-2 font-serif">
      <div class="flex">
        <div class="flex-grow">
          <EntryDetails :record="record"></EntryDetails>
        </div>
        <div>
          <button class="btn-primary rounded-br-3xl h-8 pr-10 pl-4 pr-10"
                  type="button" @click="$router.go(-1)">{{ $gettext('Close') }}</button>
        </div>
      </div>
      <hr class="my-3" />
      <div class="mb-2 text-sm" v-for="source in record.data_sources" :key="source.identifier">
        <DataSourceBox :source="source"></DataSourceBox>
        <div v-if="source.aggregated && source.aggregated.length > 0">
          <div v-for="agg in source.aggregated" :key="agg.id">
            <div @click="$router.push({ name: 'entry', params: { id: agg.entry_id } })"
            class="border rounded my-1 p-1 cursor-pointer">
              <DataSourceBox :source="agg" :short="1">{{ $gettext('Contains:') }}</DataSourceBox>
            </div>
          </div>
        </div>
        <div v-if="source.aggregations && source.aggregations.length > 0">
          <div v-for="agg in source.aggregations" :key="agg.id">
            <div @click="$router.push({ name: 'entry', params: { id: agg.entry_id } })"
            class="border rounded my-1 p-1 cursor-pointer">
              <DataSourceBox :source="agg" :short="1">{{ $gettext('Part of:') }}</DataSourceBox>
            </div>
          </div>
        </div>
      </div>
      <div v-if="record.original_entry"
           @click="$router.push({ name: 'entry', params: { id: record.original_entry.id } })"
           class="border rounded my-1 p-1 cursor-pointer">
        <EntryDetails :record="record.original_entry">{{ $gettext('Original title:') }}</EntryDetails>
      </div>
      <div v-if="record.translations && record.translations.length > 0">
        <div v-for="translation in record.translations" :key="translation.id">
          <div @click="$router.push({ name: 'entry', params: { id: translation.id } })"
            class="border rounded my-1 p-1 cursor-pointer">
            <EntryDetails :record="translation">{{ $gettext('Translation:') }}</EntryDetails>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
