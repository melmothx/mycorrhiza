<script>
 import PaginationBox from './PaginationBox.vue'
 import FacetBox from './FacetBox.vue'
 import EntryBox  from './EntryBox.vue'
 import MergeBox from './MergeBox.vue'
 import axios from 'axios'
 import { Listbox, ListboxButton, ListboxOptions, ListboxOption, } from '@headlessui/vue'
 import { ChevronUpDownIcon,  } from '@heroicons/vue/24/solid'
 export default {
     components: {
         Listbox, ListboxButton, ListboxOptions, ListboxOption,
         FacetBox, EntryBox, PaginationBox, MergeBox,
         ChevronUpDownIcon,
     },
     data() {
         const sort_directions = [
             {
                 id: "desc",
                 name: "Descending",
             },
             {
                 id: "asc",
                 name: "Ascending",
             },
         ];
         const sort_by_values = [
             {
                 id: "datestamp",
                 name: 'Sort by Acquisition Date',
             },
             {
                 id: "relevance",
                 name: 'Sort by Relevance',
             },
             {
                 id: "title",
                 name: 'Sort by Title',
             },
             {
                 id: "date",
                 name: 'Sort by Date',
             },
         ];
         return {
             matches: [],
             facets: {},
             pager: [],
             query: '',
             searched_query: '',
             total_entries: 0,
             is_authenticated: false,
             can_set_exclusions: false,
             can_merge: false,
             sort_by_values: sort_by_values,
             sort_by: sort_by_values[0],
             sort_directions: sort_directions,
             sort_direction: sort_directions[0],
         }
     },
     methods: {
         clear_all() {
             this.query = "";
             this.searched_query = "";
             this.facets = [];
             this.sort_by = this.sort_by_values[0];
             this.sort_direction = this.sort_directions[0];
             this.$router.push({ name: 'home' });
             this.get_results({}, { update_facets: 1 });
         },
         searchText() {
             let fresh = {
                 query: this.query,
                 sort_by: this.sort_by.id,
                 sort_direction: this.sort_direction.id,
             };
             this.$router.push({ name: 'home', query: fresh });
             this.get_results(fresh, { update_facets: 1 });
         },
         get_results(query, opts) {
             let params = new URLSearchParams;
             console.log(query);
             for (const pname in query) {
                 console.log(`Checking ${pname}`);
                 let pvalues = query[pname];
                 if (pvalues instanceof Array) {
                     for (const value of pvalues) {
                         if (value) {
                             console.log(`Appending ${pname} ${value}`);
                             params.append(pname, value);
                         }
                     }
                 }
                 else {
                     if (pvalues) {
                         console.log(`Appending ${pname} ${pvalues}`);
                         params.append(pname, pvalues);
                     }
                 }
             }
             console.log("Query params are ");
             console.log(params);
             axios.get('/collector/api',
                       { params: params })
                  .then((res) => {
                      this.matches = res.data.matches;
                      if (opts && opts.update_facets) {
                          this.facets = res.data.facets;
                      }
                      this.pager = res.data.pager;
                      this.total_entries = res.data.total_entries;
                      this.can_merge = res.data.can_merge;
                      this.can_set_exclusions = res.data.can_set_exclusions;
                      this.searched_query = query.query;
                  });
         },
         getResults(opts) {
             let query = { ...this.$route.query };
             console.log(query);
             this.get_results(query, opts);
         },
         getPage(page) {
             console.log(`Switching to page ${page}`);
             let query = { ...this.$route.query };
             query.page_number = page;
             this.$router.push({ name: 'home', query: query });
             this.get_results(query);
         },
         toggle_query_filter(name, term, checked) {
             console.log(`Toggling ${checked} ${name} ${term}`);
             let query = { ...this.$route.query };
             query.page_number = 1;
             // go back to the first page
             let query_name = 'filter_' + name;
             let filter_list = query[query_name] || [];
             if (!(filter_list instanceof Array)) {
                 filter_list = [ filter_list ];
             }
             if (checked) {
                 console.log(`Adding ${name} ${term} from url`);
                 filter_list.push(term);
             }
             else {
                 console.log(`Removing ${name} ${term} from url`);
                 filter_list = filter_list.filter((f) => f != term);
             }
             query[query_name] = filter_list;
             this.$router.push({ name: 'home', query: query });
             return query;
         },
         toggleFilter(name, term, checked) {
             let query = this.toggle_query_filter(name, term, checked)
             this.get_results(query);
         },
         remove_merged_filter(name, term) {
             // just update the url to avoid old crap
             toggle_query_filter(name, term, false);
         },
         handle_sorting_change() {
             // populate the url from the model and searc
             let query = { ...this.$route.query };
             query.sort_direction = this.sort_direction.id;
             query.sort_by = this.sort_by.id;
             query.page_number = 1;
             console.log("Handled sorting change");
             console.log(query);
             this.$router.push({ name: 'home', query: query });
             this.get_results(query);
         },
     },
     mounted() {
         console.log("Mounted");
         let q = { ...this.$route.query };
         // set the values from the model in the query
         this.sort_by = this.sort_by_values.find((i) => i.id == q.sort_by)
                     || this.sort_by_values[0];
         this.sort_direction = this.sort_directions.find((i) => i.id == q.sort_direction)
                            || this.sort_directions[0];
         this.query = q.query;
         this.$router.push({ name: 'home', query: q });
         this.get_results(q, { update_facets: 1 });
     },
     watch: {
         sort_by(new_s, old_s) {
             this.handle_sorting_change();
         },
         sort_direction(new_s, old_s) {
             this.handle_sorting_change();
         },
     },
     beforeRouteUpdate(to, from) {
         console.log(from.fullPath);
         console.log(to.fullPath);
     },
 }
 /*
    $gettext('Editable and printable text')
    $gettext('Bibliographical entry only')
    $gettext('Aggregated')
    $gettext('Aggregation')
    $gettext('Aggregation')
    $gettext('MERGE_AUTHOR')
    $gettext('MERGE_ENTRY')
    $gettext('SET_TRANSLATION')
    $gettext('SET_AGGREGATION')
  */
</script>
<template>
  <form class="m-1 md:m-5" @submit.prevent="searchText">
    <h1 class="text-xl text-center font-semibold m-8">
      <template v-if="searched_query">
        {{ $ngettext("Search results for %1: found %2 entry", "Search results for %1: found %2 entries", total_entries, searched_query, total_entries) }}
      </template>
      <template v-else>
        {{ $gettext('All entries (%1)', total_entries) }}
      </template>
    </h1>
    <div>
      <div class="flex h-8">
        <button class="btn-primary rounded-none h-8 px-4"
                @click="clear_all"
                type="button">
          {{ $gettext('Clear') }}
        </button>
        <input class="mcrz-input shadow"
               type="text" placeholder="Search" v-model="query"/>
        <Listbox v-model="sort_by">
          <div class="relative m-0">
            <ListboxButton class="mcrz-listbox-button"
                           v-slot="{ open }">
              <span class="block truncate">{{ $gettext(sort_by.name) }}</span>
              <span class="mcrz-select-chevron-container">
                <ChevronUpDownIcon
                    class="h-5 w-5 text-gray-400"
                    aria-hidden="true"
                />
              </span>
            </ListboxButton>
            <transition
                enter-active-class="transition duration-100 ease-out"
                enter-from-class="transform scale-95 opacity-0"
                enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-75 ease-in"
                leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0">
              <ListboxOptions class="mcrz-listbox-options">
                <ListboxOption v-for="sv in sort_by_values"
                               :value="sv" :key="sv.id"
                               class="cursor-pointer hover:text-spectra-800 py-1"
                >{{ $gettext(sv.name) }}</ListboxOption>
              </ListboxOptions>
            </transition>
          </div>
        </Listbox>
        <Listbox v-if="sort_by.id != 'relevance'" v-model="sort_direction">
          <div class="relative m-0">
            <ListboxButton class="mcrz-listbox-button"
                           v-slot="{ open }">
              <span class="block truncate">{{ $gettext(sort_direction.name) }}</span>
              <span class="mcrz-select-chevron-container">
                <ChevronUpDownIcon
                    class="h-5 w-5 text-gray-400"
                    aria-hidden="true"
                />
              </span>
            </ListboxButton>
            <transition
                enter-active-class="transition duration-100 ease-out"
                enter-from-class="transform scale-95 opacity-0"
                enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-75 ease-in"
                leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0">
              <ListboxOptions class="mcrz-listbox-options">
                <ListboxOption v-for="sd in sort_directions"
                               :value="sd" :key="sd.id"
                               class="cursor-pointer hover:text-spectra-800 py-1"
                >{{ $gettext(sd.name) }}</ListboxOption>
              </ListboxOptions>
            </transition>
          </div>
        </Listbox>
        <button class="btn-primary rounded-none rounded-br-3xl h-8 pr-10 pl-4 pr-10"
                type="submit">{{ $gettext('Search') }}</button>
      </div>
    </div>
  </form>
  <div class="m-1 md:m-5">
    <div class="grid gap-8 grid-cols-2
         md:grid-cols-[150px_auto]
         lg:grid-cols-[250px_auto_250px]">
      <div>
        <div class="sticky top-5">
          <div v-if="facets.download" class="mb-3">
            <FacetBox
                :use_sorting="false"
                :values="facets.download.values"
                :name="facets.download.name"
                @toggle-app-filter="toggleFilter"
                :translate_values="true"
            >{{ $gettext('Download Types') }}</FacetBox>
          </div>
          <div v-if="facets.aggregate" class="mb-3">
            <FacetBox
                :use_sorting="false"
                :values="facets.aggregate.values"
                :name="facets.aggregate.name"
                @toggle-app-filter="toggleFilter"
            >{{ $gettext('Aggregation') }}</FacetBox>
          </div>
          <div v-if="facets.language" class="mb-3">
            <FacetBox
                :use_sorting="true"
                :values="facets.language.values"
                :name="facets.language.name"
                @toggle-app-filter="toggleFilter"
            >{{ $gettext('Language') }}</FacetBox>
          </div>
          <div v-if="facets.library" class="mb-3">
            <FacetBox
                :use_sorting="true"
                :values="facets.library.values"
                :name="facets.library.name"
                :can_set_exclusions="can_set_exclusions"
                @toggle-app-filter="toggleFilter"
                @refetch-results="getResults({ update_facets: 1 })">
              {{ $gettext('Libraries') }}
            </FacetBox>
          </div>
          <div v-if="facets.creator" class="mb-3">
            <FacetBox
                :can_merge="can_merge"
                :use_sorting="true"
                :values="facets.creator.values"
                :name="facets.creator.name"
                @toggle-app-filter="toggleFilter">
              {{ $gettext('Authors') }}
            </FacetBox>
          </div>
          <div v-if="facets.date" class="mb-3">
            <FacetBox
                :use_sorting="true"
                :values="facets.date.values"
                :name="facets.date.name"
                @toggle-app-filter="toggleFilter">
              {{ $gettext('Date') }}
            </FacetBox>
          </div>
        </div>
      </div>
      <div>
        <PaginationBox :pager="pager" @get-page="getPage" />
        <div class="mb-2">
          <template v-for="match in matches" :key="match.entry_id">
            <EntryBox :record="match"
                      :can_set_exclusions="can_set_exclusions"
                      :can_merge="can_merge"
                      @refetch-results="getResults({ update_facets: 1 })" />
          </template>
        </div>
        <PaginationBox :pager="pager" @get-page="getPage" />
      </div>
      <div v-if="can_merge">
        <div class="sticky top-5">
          <div id="author-cards" class="mb-2">
            <MergeBox merge_type="author"
                      create_item="agent"
                      dashboard="merged-agents"
                      remove_merged_filter="creator"
                      help_text="MERGE_AUTHOR"
                      @remove-merged-filter="remove_merged_filter"
                      @refetch-results="getResults({ update_facets: 1 })">
              {{ $gettext('Merge authors here') }}
            </MergeBox>
          </div>
          <div id="title-cards" class="mb-2">
            <MergeBox merge_type="entry"
                      help_text="MERGE_ENTRY"
                      dashboard="merged-entries"
                      @refetch-results="getResults()">
              {{ $gettext('Merge entries here') }}
            </MergeBox>
          </div>
          <div id="translation-cards" class="mb-2">
            <MergeBox merge_type="entry"
                      help_text="SET_TRANSLATION"
                      dashboard="translations"
                      api_call="set-translations" @refetch-results="getResults({ update_facets: 1 })">
              {{ $gettext('Set translations here') }}
            </MergeBox>
          </div>
          <div id="aggregations-cards" class="mb-2">
            <MergeBox merge_type="entry"
                      api_call="set-aggregated"
                      help_text="SET_AGGREGATION"
                      create_item="aggregation"
                      @refetch-results="getResults()">
              {{ $gettext('Set aggregations here') }}
            </MergeBox>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
