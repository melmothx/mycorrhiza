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
                 id: "relevance",
                 name: 'Sort by Relevance',
             },
             {
                 id: "datestamp",
                 name: 'Sort by Acquisition Date',
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
             flash_success: "",
             flash_error: "",
             matches: [],
             facets: {},
             filters: [],
             pager: [],
             query: '',
             searched_query: '',
             total_entries: 0,
             current_page: 1,
             merge_entry_records: [],
             merge_author_records: [],
             is_authenticated: false,
             can_set_exclusions: false,
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
             this.current_page = 1;
             this.filters = [];
             this.facets = [];
             this.sort_by = this.sort_by_values[0];
             this.sort_direction = this.sort_directions[0];
             this.getResults({ update_facets: 1 });
         },
         clear_flash_success() {
             this.flash_success = "";
         },
         clear_flash_error() {
             this.flash_error = "";
         },
         searchText() {
             // reset page, filters
             this.current_page = 1;
             this.filters = [];
             this.facets = [];
             this.getResults({ update_facets: 1 });
         },
         parse_query_params() {
             console.log(this.$route.query);
             let q = this.$route.query;
             this.query = q.query || "";
             this.current_page = q.page_number || 1;
             this.sort_by = this.sort_by_values.find((i) => i.id == q.sort_by)
                         || this.sort_by_values[0];
             this.sort_direction = this.sort_directions.find((i) => i.id == q.sort_direction)
                                || this.sort_directions[0];
             for (const filter in q) {
                 console.log(`filter is ${filter}`);
                 if (filter.match(/^filter_/)) {
                     console.log(`matched filter is ${filter}`);
                     let fname = filter.replace(/^filter_/, '');
                     let values = q[filter];
                     console.log(fname);
                     console.log(values);
                     if (values instanceof Array) {
                         for (const value of values) {
                             this.filters.push({ name: fname, term: value });
                         }
                     }
                     else {
                         this.filters.push({ name: fname, term: values });
                     }
                 }
             }
             console.log(this.filters);
         },
         getResults(args) {
             let vm = this;
             let params = new URLSearchParams;
             params.append('query', vm.query);
             params.append('page_number', vm.current_page);
             params.append('sort_by', vm.sort_by.id);
             params.append('sort_direction', vm.sort_direction.id);
             let query = {
                 query: vm.query,
                 page_number: vm.current_page,
                 sort_by: vm.sort_by.id,
                 sort_direction: vm.sort_direction.id,
             };
             let filters = this.filters;
             for (let i = 0; i < filters.length; i++) {
                 let fname = 'filter_' + filters[i].name;
                 params.append(fname, filters[i].term);
                 query[fname] ||= [];
                 query[fname].push(filters[i].term)
             }
             this.$router.replace({ name: 'home', query: query });
             axios.get('/collector/api',
                       { params: params })
                  .then(function(res) {
                      vm.matches = res.data.matches;
                      if (args && args.update_facets) {
                          vm.facets = res.data.facets;
                      }
                      vm.pager = res.data.pager;
                      vm.total_entries = res.data.total_entries;
                      vm.is_authenticated = res.data.is_authenticated;
                      vm.can_set_exclusions = res.data.can_set_exclusions;
                      vm.searched_query = vm.query;
                  });
         },
         getPage(page) {
             this.current_page = page;
             this.getResults();
         },
         toggleFilter(name, term, checked) {
             console.log(`Toggling ${checked} ${name} ${term}`);
             // go back to the first page
             this.current_page = 1;
             if (checked) {
                 this.filters.push({ 'name': name, 'term': term });
             }
             else {
                 this.filters = this.filters.filter((f) => f.name != name || f.term != term)
             }
             this.getResults();
         },
         remove_merged_filter(name, term) {
             console.log(`Removing ${term} ${name}`);
             this.filters = this.filters.filter((f) => f.name != name || f.term != term)
         }
     },
     mounted() {
         this.parse_query_params();
         this.getResults({ update_facets: 1 });
     },
     watch: {
         sort_by(new_s, old_s) {
             this.getResults();
         },
         sort_direction(new_s, old_s) {
             this.getResults();
         },
     }
 }
 /*
    $gettext('Editable and printable text')
    $gettext('Bibliographical entry only')
    $gettext('Aggregated')
    $gettext('Aggregation')
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
    <div v-if="flash_success" class="bg-green-100 border-green-600 text-green-800 border rounded p-2 flex justify-center cursor-pointer"
         @click="clear_flash_success">
      {{ flash_success }}
    </div>
    <div v-if="flash_error" class="bg-red-100 border-red-600 text-red-800 border rounded p-2 flex justify-center cursor-pointer"
         @click="clear_flash_error">
      {{ flash_error }}
    </div>

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
            <ListboxButton class="relative w-full cursor-pointer py-1 h-8 pl-3 pr-10 text-left shadow-md text-sm
                                  bg-perl-bush-50"
                           v-slot="{ open }">
              <span class="block truncate">{{ $gettext(sort_by.name) }}</span>
              <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
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
              <ListboxOptions class="absolute mt-1 max-h-60 w-full overflow-auto bg-perl-bush-50 pl-3 text-sm shadow-lg z-40">
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
            <ListboxButton class="relative w-full cursor-pointer py-1 h-8 pl-3 pr-10 text-left shadow-md text-sm
                                  bg-perl-bush-50"
                           v-slot="{ open }">
              <span class="block truncate">{{ $gettext(sort_direction.name) }}</span>
              <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
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
              <ListboxOptions class="absolute mt-1 max-h-60 w-full overflow-auto bg-perl-bush-50 pl-3 shadow-lg text-sm z-40">
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
                :can_merge="is_authenticated"
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
                      :can_merge="is_authenticated"
                      @refetch-results="getResults({ update_facets: 1 })" />
          </template>
        </div>
        <PaginationBox :pager="pager" @get-page="getPage" />
      </div>
      <div v-if="is_authenticated">
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
