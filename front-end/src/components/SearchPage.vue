<script>
 import PaginationBox from './PaginationBox.vue'
 import FacetBox from './FacetBox.vue'
 import FacetBoxHeader from './FacetBoxHeader.vue'
 import EntryBox  from './EntryBox.vue'
 import MergeBox from './MergeBox.vue'
 import SingleFilterBox from './SingleFilterBox.vue'
 import axios from 'axios'
 import { Listbox, ListboxButton, ListboxOptions, ListboxOption, } from '@headlessui/vue'
 import { ChevronUpDownIcon, XCircleIcon, XMarkIcon, ListBulletIcon } from '@heroicons/vue/24/solid'
 export default {
     components: {
         Listbox, ListboxButton, ListboxOptions, ListboxOption,
         FacetBoxHeader,
         FacetBox, EntryBox, PaginationBox, MergeBox,
         ChevronUpDownIcon, XCircleIcon, XMarkIcon,
         ListBulletIcon,
         SingleFilterBox,
     },
     data() {
         const sort_by_values = [
             {
                 id: "datestamp",
                 name: 'Sort by Acquisition Date',
                 highlight: false,
             },
             {
                 id: "relevance",
                 name: 'Sort by Relevance',
                 highlight: false,
             },
             {
                 id: "title_asc",
                 name: 'Sort by Title (A-Z)',
                 highlight: true,
             },
             {
                 id: "title_desc",
                 name: 'Sort by Title (Z-A)',
                 highlight: true,
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
             active_filters: [],
             search_was_run: false,
             single_filter_boxes: [],
         }
     },
     methods: {
         adjust_sorting() {
             if (this.query && this.sort_by.id == 'datestamp') {
                 this.sort_by = this.sort_by_values.find((i) => i.id == 'relevance');
             }
             else if (!this.query && this.sort_by.id == 'relevance') {
                 this.sort_by = this.sort_by_values.find((i) => i.id == 'datestamp');
             }
         },
         active_sort_by_values() {
             console.log("Called active_sort_by_values");
             if (this.query) {
                 return this.sort_by_values.filter((f) => f.id != 'datestamp');
             }
             else {
                 return this.sort_by_values.filter((f) => f.id != 'relevance');
             }
         },
         run_search(query) {
             console.log("Running search");
             console.log(query);
             this.adjust_sorting();
             query.query = this.query;
             query.page_number = 1;
             query.sort_by = this.sort_by.id;
             this.$router.push({ name: 'search', query: query });
             this.get_results(query, { update_facets: true });
         },
         clear_filters() {
             if (this.query) {
                 this.sort_by = this.sort_by_values.find((i) => i.id == 'relevance');
             }
             else {
                 this.sort_by = this.sort_by_values.find((i) => i.id == 'datestamp');
             }
             this.run_search({});
         },
         refine() {
             // same as above, but picks the parameters from the url
             this.run_search({ ...this.$route.query });
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
                      this.searched_query = res.data.pretty_query || query.query;
                      if (opts && opts.scroll) {
                          document.getElementById('result-box').scrollIntoView({ behavior: "smooth" });
                      }
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
             this.get_results(query, { scroll: true });
         },
         toggle_query_filter(name, term, checked) {
             console.log(`Toggling ${checked} ${name} ${term}`);
             let query = { ...this.$route.query };
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
         this.adjust_sorting();
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
    $gettext('__MERGE_AUTHOR__')
    $gettext('__MERGE_ENTRY__')
    $gettext('__SET_TRANSLATION__')
    $gettext('__SET_AGGREGATION__')
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
    <div class="sm:hidden" v-for="sf in single_filter_boxes">
      <SingleFilterBox :key="sf.name + sf.id" :id="sf.id" :name="sf.name" :editable="can_merge" />
    </div>

    <div v-if="active_filters" class="mb-4 flex flex-wrap place-content-center">
      <template v-for="af in active_filters">
        <div class="btn-primary mr-2 my-1 p-1 rounded-sm flex cursor-pointer text-sm"
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
        <div class="relative w-full">
          <input class="mcrz-input shadow-sm w-full my-1 sm:my-0 sm:h-8"
                 type="text" :placeholder="$gettext('Search')" v-model="query"/>
          <button v-if="query" type="button"
                  @click="query = ''"
                  class="absolute inset-y-0 right-0 flex items-center pr-3 font-bold
                        text-claret-800 hover:text-claret-600 cursor-pointer">
            &#10005;
          </button>
        </div>
        <Listbox v-model="sort_by" @click="refine()">
          <div class="relative m-0">
            <ListboxButton class="mcrz-listbox-button"
                           v-slot="{ open }">
              <span v-if="sort_by.highlight" class="block truncate text-claret-800 font-bold">{{ $gettext(sort_by.name) }}</span>
              <span v-else class="block truncate">{{ $gettext(sort_by.name) }}</span>
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
                <ListboxOption v-for="sv in active_sort_by_values()"
                               :value="sv" :key="sv.id"
                               class="cursor-pointer hover:text-spectra-800 py-1"
                >{{ $gettext(sv.name) }}</ListboxOption>
              </ListboxOptions>
            </transition>
          </div>
        </Listbox>
        <button class="btn-primary rounded-none h-8 px-4 w-full sm:w-auto sm:border-r"
                @click="clear_filters"
                type="button">
          {{ $gettext('Clear') }}
        </button>
        <button class="btn-primary rounded-none h-8 px-4 w-full  sm:w-auto sm:rounded-br-3xl sm:pr-10 sm:pl-4"
                type="button"
                @click="refine">{{ $gettext('Search') }}</button>
      </div>
    </div>
  </form>
  <div class="m-1 md:m-5">
    <div class="grid gap-8
                grid-cols-1
                sm:grid-cols-[250px_auto]
                lg:grid-cols-[250px_auto_250px]">
      <div class="hidden sm:block">
        <div class="sm:sticky sm:top-5">
          <div v-if="facets.language" class="mb-3">
            <FacetBox
                :use_sorting="true"
                :values="facets.language.values"
                :name="facets.language.name"
                @toggle-app-filter="toggleFilter">
              <FacetBoxHeader :title="$gettext('Language')" />
            </FacetBox>
          </div>
          <div v-if="facets.creator" class="mb-3">
            <FacetBox
                :can_merge="can_merge"
                :use_sorting="true"
                :values="facets.creator.values"
                :name="facets.creator.name"
                @toggle-app-filter="toggleFilter">
              <FacetBoxHeader link_name="agent_overview" :title="$gettext('Authors')" />
            </FacetBox>
          </div>
          <div v-else class="mb-3">
            <FacetBoxHeader link_name="agent_overview" :title="$gettext('Authors')" />
          </div>
          <div v-if="facets.library" class="mb-3">
            <FacetBox
                :use_sorting="true"
                :values="facets.library.values"
                :name="facets.library.name"
                :can_set_exclusions="can_set_exclusions"
                @toggle-app-filter="toggleFilter"
                @refetch-results="getResults({ update_facets: 1 })">
              <FacetBoxHeader link_name="library_overview" :title="$gettext('Libraries')" />
            </FacetBox>
          </div>
          <div v-else class="mb-3">
            <FacetBoxHeader link_name="library_overview" :title="$gettext('Libraries')" />
          </div>
          <div v-if="facets.date" class="mb-3">
            <FacetBox
                :use_sorting="true"
                :values="facets.date.values"
                :name="facets.date.name"
                @toggle-app-filter="toggleFilter">
              <FacetBoxHeader :title="$gettext('Date')" />
            </FacetBox>
          </div>
          <div v-if="facets.download" class="mb-3">
            <FacetBox
                :use_sorting="false"
                :values="facets.download.values"
                :name="facets.download.name"
                @toggle-app-filter="toggleFilter"
                :translate_values="true">
              <FacetBoxHeader :title="$gettext('Download Types')" />
            </FacetBox>
          </div>
          <div v-if="facets.aggregate" class="mb-3">
            <FacetBox
                :use_sorting="false"
                :values="facets.aggregate.values"
                :name="facets.aggregate.name"
                @toggle-app-filter="toggleFilter">
              <FacetBoxHeader :title="$gettext('Aggregations')" />
            </FacetBox>
          </div>
        </div>
      </div>
      <div id="result-box">
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
      <div class="hidden sm:block">
        <div v-for="sf in single_filter_boxes">
          <SingleFilterBox :key="sf.name + sf.id" :id="sf.id" :name="sf.name" :editable="can_merge" />
        </div>
        <div v-if="can_merge" class="sticky top-5">
          <div id="author-cards" class="mb-2">
            <MergeBox merge_type="author"
                      create_item="agent"
                      dashboard="merged-agents"
                      remove_merged_filter="creator"
                      help_text="__MERGE_AUTHOR__"
                      @remove-merged-filter="remove_merged_filter"
                      @refetch-results="no_op">
              {{ $gettext('Merge authors here') }}
            </MergeBox>
          </div>
          <div id="split-authors" class="mb-2">
            <MergeBox merge_type="author"
                      api_call="split-author"
                      create_item="agent"
                      dashboard="splat-agents"
                      help_text="__SPLIT_AUTHOR__">
              {{ $gettext('Split authors here') }}
            </MergeBox>
          </div>
          <div id="title-cards" class="mb-2">
            <MergeBox merge_type="entry"
                      help_text="__MERGE_ENTRY__"
                      dashboard="merged-entries"
                      @refetch-results="getResults()">
              {{ $gettext('Merge entries here') }}
            </MergeBox>
          </div>
          <div id="translation-cards" class="mb-2">
            <MergeBox merge_type="entry"
                      help_text="__SET_TRANSLATION__"
                      dashboard="translations"
                      api_call="set-translations" @refetch-results="getResults({ update_facets: 1 })">
              {{ $gettext('Set translations here') }}
            </MergeBox>
          </div>
          <div id="aggregations-cards" class="mb-2">
            <MergeBox merge_type="entry"
                      api_call="set-aggregated"
                      help_text="__SET_AGGREGATION__"
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
