<script>
 import PaginationBox from './PaginationBox.vue'
 import FacetBox from './FacetBox.vue'
 import EntryBox  from './EntryBox.vue'
 import MergeBox from './MergeBox.vue'
 import axios from 'axios'
 export default {
     components: { FacetBox, EntryBox, PaginationBox, MergeBox },
     data() {
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
             sort_by: "created",
             sort_direction: "desc",
         }
     },
     methods: {
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
             this.getResults(1);
         },
         getResults(update_facets) {
             let vm = this;
             let params = new URLSearchParams;
             params.append('query', vm.query);
             params.append('page_number', vm.current_page);
             params.append('sort_by', vm.sort_by);
             params.append('sort_direction', vm.sort_direction);
             let filters = this.filters;
             for (let i = 0; i < filters.length; i++) {
                 params.append('filter_' +  filters[i].name, filters[i].term);
             }
             axios.get('/search/api',
                       { params: params })
                  .then(function(res) {
                      vm.matches = res.data.matches;
                      if (update_facets) {
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
         this.searchText();
     },
     computed: {
     },
 }
</script>
<template>
  <form class="m-1 md:m-5" @submit.prevent="searchText">
    <h1 class="text-3xl text-center font-semibold m-8">
      <template v-if="searched_query">
        Search results for {{ searched_query }} ({{ total_entries }})
      </template>
      <template v-else>
        All entries ({{ total_entries }})
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
      <div class="flex my-5">
        <input class="outline
                      outline-0
                      border
                      border-gray-300
                      focus:border-pink-500
                      focus:ring-0
                      px-2
                      rounded-l flex-grow"
               type="text" placeholder="Search" v-model="query"/>
        <select v-model="sort_by"
                @change="getResults()"
                class="outline
                         outline-0
                         border
                         border-gray-300
                         focus:border-pink-500
                         focus:ring-0">
          <option value="">Sort by Relevance</option>
          <option value="title">Sort by Title</option>
          <option value="date">Sort by Date</option>
          <option value="created">Sort by Acquisition Date</option>
        </select>
        <select v-if="sort_by"
                v-model="sort_direction"
                @change="getResults()"
                class="outline
                      outline-0
                      border
                      border-gray-300
                      focus:border-pink-500
                      focus:ring-0">
          <option value="asc">Asc</option>
          <option value="desc">Des</option>
        </select>
        <button class="rounded-r bg-pink-500
                       hover:bg-pink-700 text-white
                       font-semibold mr-1 py-2 px-6 h-11"
                type="submit">Search</button>
      </div>
    </div>
  </form>
  <div class="m-1 md:m-5">
    <div class="grid gap-2 grid-cols-[300px_auto_300px]">
      <div>
        <div class="sticky top-5">
          <div v-if="facets.language" class="mb-3">
            <FacetBox
                :values="facets.language.values"
                :name="facets.language.name"
                @toggle-app-filter="toggleFilter"
            >Language</FacetBox>
          </div>
          <div v-if="facets.library" class="mb-3">
            <FacetBox
                :values="facets.library.values"
                :name="facets.library.name"
                :can_set_exclusions="can_set_exclusions"
                @toggle-app-filter="toggleFilter"
                @refetch-results="getResults(1)">
            Libraries</FacetBox>
          </div>
          <div v-if="facets.creator" class="mb-3">
            <FacetBox
                :values="facets.creator.values"
                :name="facets.creator.name"
                @toggle-app-filter="toggleFilter"
            >Authors</FacetBox>
          </div>
          <div v-if="facets.date" class="mb-3">
            <FacetBox
                :values="facets.date.values"
                :name="facets.date.name"
                @toggle-app-filter="toggleFilter"
            >Date</FacetBox>
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
                      @refetch-results="getResults(1)" />
          </template>
        </div>
        <PaginationBox :pager="pager" @get-page="getPage" />
      </div>
      <div v-if="is_authenticated">
        <div class="sticky top-5">
          <div id="author-cards" class="mb-2">
            <MergeBox merge_type="author"
                      remove_merged_filter="creator"
                      @remove-merged-filter="remove_merged_filter"
                      @refetch-results="getResults(1)">
              Merge authors here
            </MergeBox>
          </div>
          <div id="title-cards" class="mb-2">
            <MergeBox merge_type="entry" @refetch-results="getResults()">
              Merge entries here
            </MergeBox>
          </div>
          <div id="translation-cards" class="mb-2">
            <MergeBox merge_type="entry" api_call="set-translations" @refetch-results="getResults()">
              Set translations here
            </MergeBox>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
