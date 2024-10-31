<script>
 import PaginationBox from './PaginationBox.vue'
 import FacetBox from './FacetBox.vue'
 import EntryBox  from './EntryBox.vue'
 import MergeBox from './MergeBox.vue'
 import SingleFilterBox from './SingleFilterBox.vue'
 import axios from 'axios'
 import { Listbox, ListboxButton, ListboxOptions, ListboxOption, } from '@headlessui/vue'
 import { ChevronUpDownIcon, XCircleIcon, XMarkIcon, ListBulletIcon } from '@heroicons/vue/24/solid'
 export default {
     components: {
         Listbox, ListboxButton, ListboxOptions, ListboxOption,
         FacetBox, EntryBox, PaginationBox, MergeBox,
         ChevronUpDownIcon, XCircleIcon, XMarkIcon,
         ListBulletIcon,
         SingleFilterBox,
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
             active_filters: [],
             search_was_run: false,
             single_filter_boxes: [],
         }
     },
     methods: {
         clear_all() {
             this.query = "";
             this.searched_query = "";
             this.facets = [];
             this.sort_by = this.sort_by_values[0];
             this.sort_direction = this.sort_directions[0];
             this.$router.push({ name: 'search' });
             this.get_results({}, { update_facets: true });
         },
         refine() {
             let query = { ...this.$route.query };
             query.query = this.query;
             query.page_number = 1;
             query.sort_by = this.sort_by.id;
             query.sort_direction = this.sort_direction.id;
             this.$router.push({ name: 'search', query: query });
             this.get_results(query, { update_facets: true });
         },
         searchText() {
             let fresh = {
                 query: this.query,
                 sort_by: this.sort_by.id,
                 sort_direction: this.sort_direction.id,
             };
             this.$router.push({ name: 'search', query: fresh });
             this.get_results(fresh, { update_facets: true });
         },
         get_results(query, opts) {
             let params = new URLSearchParams;
             console.log(query);
             // it seems I can't remove this stupid thing
             if (opts && opts.update_facets) {
                 this.facets = [];
             }
             for (const pname in query) {
                 let pvalues = query[pname];
                 if (pvalues instanceof Array) {
                     for (const value of pvalues) {
                         if (value) {
                             params.append(pname, value);
                         }
                     }
                 }
                 else {
                     if (pvalues) {
                         params.append(pname, pvalues);
                     }
                 }
             }
             axios.get('/collector/api/search',
                       { params: params })
                  .then((res) => {
                      this.search_was_run = true;
                      this.matches = res.data.matches;
                      if (opts && opts.update_facets) {
                          this.facets = res.data.facets;
                      }
                      this.active_filters = [];
                      this.single_filter_boxes = [];
                      for (const fn of [ 'library', 'language', 'creator', 'date', 'download', 'aggregate', ]) {
                          let facet = res.data.facets[fn];
                          let count = 0;
                          if (facet) {
                              for (const ff of res.data.facets[fn].values) {
                                  if (ff.active) {
                                      this.active_filters.push({
                                          term: ff.term,
                                          id: ff.id,
                                          name: fn,
                                      });
                                      count++;
                                  }
                              }
                          }
                          if (count == 1) {
                              let idx = this.active_filters.length - 1;
                              this.single_filter_boxes.push({
                                  ...this.active_filters[idx]
                              })
                          }
                      }
                      const qre = /\b(library|creator):([0-9]+)\b/g;
                      let match;
                      while ((match = qre.exec(res.data.querystring)) !== null) {
                          console.log(match);
                          this.single_filter_boxes.push({
                              name: match[1],
                              id: match[2],
                          })
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
             this.$router.push({ name: 'search', query: query });
             this.get_results(query);
         },
         toggle_query_filter(name, term, checked) {
             console.log(`Toggling ${checked} ${name} ${term}`);
             let query = { ...this.$route.query };
             query.sort_direction = this.sort_direction.id;
             query.sort_by = this.sort_by.id;
             query.page_number = 1;
             // go back to the first page
             let query_name = 'filter_' + name;
             let filter_list = query[query_name] || [];
             if (!(filter_list instanceof Array)) {
                 filter_list = [ filter_list ];
             }
             if (checked) {
                 console.log(`Adding ${name} ${term} from url`);
                 filter_list = [ ...filter_list, `${term}` ];
             }
             else {
                 console.log(`Removing ${name} ${term} from url`);
                 filter_list = filter_list.filter((f) => f != term);
             }
             query[query_name] = filter_list;
             this.$router.push({ name: 'search', query: query });
             return query;
         },
         remove_filter_and_reload_facets(name, term) {
             let query = this.toggle_query_filter(name, term, false);
             this.get_results(query, { update_facets: true });
         },
         toggleFilter(name, term, checked) {
             let query = this.toggle_query_filter(name, term, checked)
             this.get_results(query);
         },
         remove_merged_filter(name, terms) {
             let query = { ...this.$route.query };
             let query_name = 'filter_' + name;
             console.log(`Removing ${query_name} from url`);
             delete query[query_name];
             query.page_number = 1;
             this.$router.push({ name: 'search', query: query });
             this.get_results(query, { update_facets: true });
         },
         no_op() {
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
         this.$router.push({ name: 'search', query: q });
         this.get_results(q, { update_facets: true });
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
  <form class="m-1 md:m-5" @submit.prevent="refine">
    <h1 v-if="search_was_run" class="text-xl text-center font-semibold mt-8 mb-2">
      <template v-if="searched_query">
        {{ $ngettext("Search results for “%1”: found %2 entry", "Search results for “%1”: found %2 entries", total_entries, searched_query, total_entries) }}
      </template>
      <template v-else>
        {{ $gettext('All entries (%1)', total_entries) }}
      </template>
    </h1>
    <div v-if="active_filters" class="mb-4 flex flex-wrap place-content-center">
      <template v-for="af in active_filters">
        <div class="btn-primary mr-2 my-1 p-1 rounded flex cursor-pointer text-sm"
             :title="$gettext('Click to remove the filter')"
             @click="remove_filter_and_reload_facets(af.name, af.id)">
          <div>
            {{ af.term }}
          </div>
          <div class="h-3 w-3 m-1">
            <XMarkIcon />
          </div>
        </div>
      </template>
    </div>
    <div>
      <div class="sm:flex sm:flex-nowrap sm:flex-nowrap sm:h-8">
        <button class="btn-primary rounded-none h-8 px-4 w-full sm:w-auto"
                @click="refine"
                type="button">
          {{ $gettext('Refine') }}
        </button>
        <input class="mcrz-input shadow w-full my-1 sm:my-0"
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
        <button class="btn-primary rounded-none rounded-br-3xl h-8 pr-10 pl-4 pr-10 w-full sm:w-auto"
                type="button"
                @click="searchText">{{ $gettext('Search') }}</button>
      </div>
    </div>
  </form>
  <div class="m-1 md:m-5">
    <div class="grid gap-8 grid-cols-2
                sm:grid-cols-[250px_auto]
                lg:grid-cols-[250px_auto_250px]">
      <div>
        <div class="sticky top-5">
          <div v-if="facets.language" class="mb-3">
            <FacetBox
                :use_sorting="true"
                :values="facets.language.values"
                :name="facets.language.name"
                @toggle-app-filter="toggleFilter"
            >{{ $gettext('Language') }}</FacetBox>
          </div>
          <div v-if="facets.creator" class="mb-3">
            <FacetBox
                :can_merge="can_merge"
                :use_sorting="true"
                :values="facets.creator.values"
                :name="facets.creator.name"
                @toggle-app-filter="toggleFilter">
              <router-link :to="{ name: 'agent_overview' }" class="hover:underline flex">
                <span class="flex-grow"></span>
                {{ $gettext('Authors') }}
                <ListBulletIcon class="h-4 w-4 ml-1 mt-px" />
              </router-link>
            </FacetBox>
          </div>
          <div v-if="facets.library" class="mb-3">
            <FacetBox
                :use_sorting="true"
                :values="facets.library.values"
                :name="facets.library.name"
                :can_set_exclusions="can_set_exclusions"
                @toggle-app-filter="toggleFilter"
                @refetch-results="getResults({ update_facets: 1 })">
              <router-link :to="{ name: 'library_overview' }" class="hover:underline flex">
                <span class="flex-grow"></span>
                {{ $gettext('Libraries') }}
                <ListBulletIcon class="h-4 w-4 ml-1 mt-px" />
              </router-link>
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
        <div v-if="search_was_run && (!matches || matches.length == 0)" class="font-bold text-xl">
          {{ $gettext('No result found!') }}
        </div>
        <PaginationBox :pager="pager" @get-page="getPage" />
      </div>
      <div>
        <div v-for="sf in single_filter_boxes">
          <SingleFilterBox :key="sf.name + sf.id" :id="sf.id" :name="sf.name" :editable="can_merge" />
        </div>
        <div v-if="can_merge" class="sticky top-5">
          <div id="author-cards" class="mb-2">
            <MergeBox merge_type="author"
                      create_item="agent"
                      dashboard="merged-agents"
                      remove_merged_filter="creator"
                      help_text="MERGE_AUTHOR"
                      @remove-merged-filter="remove_merged_filter"
                      @refetch-results="no_op">
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
