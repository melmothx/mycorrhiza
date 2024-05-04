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
             languages: [],
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
                          vm.compute_languages();
                      });
             }
             else {
                 console.log("Resetting");
                 vm.record = {}
             }
         },
         compute_languages() {
             const translations = this.record.translations || [];
             const languages = [];
             let orig = this.record.original_entry;
             if (orig) {
                 orig.languages.forEach((l, i) => {
                     languages.push({
                         entry_id: orig.id,
                         lang_id: l.id,
                         id: `${orig.id}-${l.id}`,
                         original: true,
                     });
                 });
             }
             translations.forEach((entry, index) => {
                 entry.languages.forEach((l, i) => {
                     languages.push({
                         entry_id: entry.id,
                         lang_id: l.id,
                         id: `${entry.id}-${l.id}`,
                         original: false,
                     });
                 });
             });
             console.log(languages);
             this.languages = languages;
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
  <div>
    <div class="m-5 p-2">
      <div class="mb-2 flex">
        <div class="flex-grow">
          <EntryDetails :record="record" />
        </div>
        <div class="ml-4" >
          <button class="btn-primary rounded-br-3xl h-8 pr-10 pl-4 pr-10"
                  type="button" @click="$router.push({ name: 'home' })">
            {{ $gettext('Back') }}
          </button>
        </div>
      </div>
      <div class="my-2 border rounded text-sm bg-perl-bush-50 shadow-md p-2" v-if="languages && languages.length > 0">
        <div class="flex">
          <h5 class="font-bold mr-2">
            {{ $gettext('Other languages:') }}
          </h5>
          <span v-for="lang in languages" :key="lang.id">
            <span class="cursor-pointer mr-2 p-1 rounded shadow-md"
                  :title="lang.original ? $gettext('Original') : $gettext('Translation')"
                  :class="lang.original ? 'btn-accent' : 'btn-primary'"
                @click="$router.push({ name: 'entry', params: { id: lang.entry_id } })">
              {{ lang.lang_id }}
            </span>
          </span>
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
    </div>
  </div>
</template>
