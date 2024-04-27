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
  <div class="bg-gradient-to-tr from-perl-bush-100 to-perl-bush-200">
    <div class="m-5 p-2">
      <div class="mb-4 pb-4 grid grid-cols-2 items-stretch">
        <div>
          <EntryDetails :record="record" show_translations="true" />
        </div>
        <div class="justify-self-end">
          <div class="mt-2 flex flex-wrap justify-start" v-if="record.translations && record.translations.length > 0">
            <h5 class="mr-2">{{ $gettext('Other languages:') }}</h5>
            <span class="btn-primary cursor-pointer mr-1 px-1 rounded shadow-md"
                  v-for="translation in record.translations" :key="translation.id">
              <span @click="$router.push({ name: 'entry', params: { id: translation.id } })">
                <span v-for="l in translation.languages" :key="l.id">
                  {{ l.value }}
                </span>
              </span>
            </span>
          </div>
        </div>
      </div>
      <div class="mb-2 text-sm shadow-md" v-for="source in record.data_sources" :key="source.identifier">
        <DataSourceBox :source="source"></DataSourceBox>
        <div v-if="source.aggregated && source.aggregated.length > 0">
          <div v-for="agg in source.aggregated" :key="agg.id">
            <div @click="$router.push({ name: 'entry', params: { id: agg.entry_id } })"
            class="p-4 cursor-pointer">
              <DataSourceBox :source="agg" :short="true">{{ $gettext('Contains:') }}</DataSourceBox>
            </div>
          </div>
        </div>
        <div v-if="source.aggregations && source.aggregations.length > 0">
          <div v-for="agg in source.aggregations" :key="agg.id">
            <div @click="$router.push({ name: 'entry', params: { id: agg.entry_id } })"
            class="p-4 cursor-pointer">
              <DataSourceBox :source="agg" :short="true">{{ $gettext('Part of:') }}</DataSourceBox>
            </div>
          </div>
        </div>
      </div>
      <div v-if="record.original_entry"
           @click="$router.push({ name: 'entry', params: { id: record.original_entry.id } })"
           class="border rounded my-1 p-1 cursor-pointer text-sm bg-perl-bush-50 shadow-md">
        <EntryDetails :record="record.original_entry">{{ $gettext('Original title:') }}</EntryDetails>
      </div>
    </div>
  </div>
</template>
