<script>
 import EntryDetails from './EntryDetails.vue'
 import DataSourceBox from './DataSourceBox.vue'
 import DataSourceShortBox from './DataSourceShortBox.vue'
 import BackButton from './BackButton.vue'
 import { Cog8ToothIcon } from '@heroicons/vue/24/solid'
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     props: [ 'entry_id' ],
     components: {
         EntryDetails,
         DataSourceBox,
         DataSourceShortBox,
         BackButton,
         Cog8ToothIcon,
     },
     data() {
         return {
             record: {},
             languages: [],
             has_data_sources: true,
             query_is_running: false,
         }
     },
     methods: {
         fetch_record() {
             this.query_is_running = true;
             document.getElementById('app').scrollIntoView({ behavior: "smooth" });
             this.record = {}
             this.has_data_sources = false;
             if (this.entry_id) {
                 axios.get('/collector/api/entry/' + this.entry_id)
                      .then((res) => {
                          this.record = res.data;
                          this.compute_languages();
                          this.query_is_running = false;
                          if (this.entry_id != this.record.id) {
                              console.log(`Redirecting from ${this.entry_id} to ${this.record.id}`);
                              this.$router.push({ name: 'entry', params: { id: this.record.id } });
                          }
                          if (this.record.data_sources && this.record.data_sources.length) {
                              this.has_data_sources = true;
                          }
                          else {
                              this.has_data_sources = false;
                          }
                      })
                      .catch((res) => {
                          this.query_is_running = false;
                      });
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
  <div v-if="query_is_running" class="font-bold flex items-center justify-center">
    <div class="flex">
      <Cog8ToothIcon class="h-4 m-1 animate-spin" />
      {{ $gettext('Fetching results, hold on...') }}
      <Cog8ToothIcon class="h-4 m-1 animate-spin" />
    </div>
  </div>
  <div v-if="has_data_sources">
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
        <div v-if="source.aggregated && source.aggregated.length > 0" class="p-2">
          <div class="mt-2 flex bg-linear-to-tr from-old-copper-300 to-old-copper-200 px-2 py-2 rounded-t">
            <h2 class="font-semibold my-2">{{ $gettext('Contains:') }}</h2>
          </div>
          <div v-for="agg in source.aggregated" :key="agg.id" class="py-2 border-b border-old-copper-200">
            <router-link :to="{ name: 'entry', params: { id: agg.entry_id } }">
              <DataSourceShortBox :source="agg" />
            </router-link>
          </div>
        </div>
        <div v-if="source.aggregations && source.aggregations.length > 0" class="p-2">
          <div class="mt-2 flex bg-linear-to-tr from-old-copper-300 to-old-copper-200 px-2 py-2 rounded-t">
            <h2 class="font-semibold my-2">{{ $gettext('Part of:') }}</h2>
          </div>
          <div v-for="agg in source.aggregations" :key="agg.id" class="py-2 border-b border-old-copper-200">
            <router-link :to="{ name: 'entry', params: { id: agg.entry_id } }">
              <DataSourceShortBox :source="agg" />
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else-if="!query_is_running">
    <div class="m-8 p-2 text-center">
      <strong class="text-xl">{{ $gettext('Sorry! We could not found this entry!')  }}</strong>
      <p class="mt-8">
        {{ $gettext('The entry does not exist, it was deleted or it is not public any more') }}
      </p>
    </div>
  </div>
</template>
