<script>
 import EntryDetails from './EntryDetails.vue'
 import DataSourceBox from './DataSourceBox.vue'
 import BackButton from './BackButton.vue'
 import axios from 'axios'
 export default {
     props: [ 'entry_id' ],
     components: { EntryDetails, DataSourceBox, BackButton },
     data() {
         return {
             record: {},
             languages: [],
         }
     },
     methods: {
         fetch_record() {
             if (this.entry_id) {
                 axios.get('/collector/api/entry/' + this.entry_id)
                      .then((res) => {
                          this.record = res.data;
                          this.compute_languages();
                          if (this.entry_id !== this.record.id) {
                              console.log("Redirecting");
                              this.$router.push({ name: 'entry', params: { id: this.record.id } });
                          }
                      });
             }
             else {
                 console.log("Resetting");
                 this.record = {}
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
        <div class="grow">
          <EntryDetails :record="record" />
        </div>
        <div class="ml-4" >
          <BackButton />
        </div>
      </div>
      <div class="my-2 border rounded-sm text-sm bg-perl-bush-50 shadow-md p-2" v-if="languages && languages.length > 0">
        <div class="flex">
          <h5 class="font-bold mr-2">
            {{ $gettext('Other languages:') }}
          </h5>
          <span v-for="lang in languages" :key="lang.id">
            <router-link class="cursor-pointer mr-2 p-1 rounded-sm shadow-md"
                  :title="lang.original ? $gettext('Original') : $gettext('Translation')"
                  :class="lang.original ? 'btn-accent' : 'btn-primary'"
                  :to="{ name: 'entry', params: { id: lang.entry_id } }">
              {{ lang.lang_id }}
            </router-link>
          </span>
        </div>
      </div>
      <div class="mb-2 text-sm shadow-md" v-for="source in record.data_sources" :key="source.identifier">
        <DataSourceBox :source="source"></DataSourceBox>
        <div v-if="source.aggregated && source.aggregated.length > 0">
          <div v-for="agg in source.aggregated" :key="agg.id" class="p-4">
            <router-link :to="{ name: 'entry', params: { id: agg.entry_id } }">
              <DataSourceBox :source="agg" :short="true">{{ $gettext('Contains:') }}</DataSourceBox>
            </router-link>
          </div>
        </div>
        <div v-if="source.aggregations && source.aggregations.length > 0">
          <div v-for="agg in source.aggregations" :key="agg.id" class="p-4">
            <router-link :to="{ name: 'entry', params: { id: agg.entry_id } }">
              <DataSourceBox :source="agg" :short="true">{{ $gettext('Part of:') }}</DataSourceBox>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
