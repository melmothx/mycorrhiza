<script>
 import Pagination from './components/Pagination.vue'
 import Facet from './components/Facet.vue'
 import Entry  from './components/Entry.vue'
 import axios from 'axios'
 export default {
     components: { Facet, Entry, Pagination },
     data() {
         return {
             flash_success: "",
             flash_error: "",
             matches: [],
             facets: [],
             filters: [],
             pager: [],
             query: '',
             total_entries: 0,
             current_page: 1,
             limit_facets: 0,
             merge_entry_records: [],
             merge_author_records: [],
             is_authenticated: false,
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
                  });
         },
         getPage(page) {
             this.current_page = page;
             this.getResults();
         },
         toggleFilter(term, name, checked) {
             console.log(`Toggling ${checked} ${name} ${term}`);
             // go back to the first page
             this.current_page = 1;
             if (checked) {
                 this.filters.push({ 'name': name, 'term': term });
             }
             else {
                 this.filters = this.filters.filter((f) => f.name != name && f.term != term)
             }
             this.getResults();
         },
         onEntryDrop(e) {
             if (e) {
                 const entry = e.dataTransfer.getData('Entry');
                 const title = e.dataTransfer.getData('EntryTitle');
                 if (entry && title) {
                     console.log("Dropping entry: " + entry + " " + title);
                     this.merge_entry_records.push({ "entry_id": entry,
                                                    "title": title,
                     });
                 }
             }
         },
         onAuthorDrop(e) {
             if (e) {
                 const author = e.dataTransfer.getData('Author');
                 if (author) {
                     console.log("Dropping author " + author);
                     this.merge_author_records.push(author);
                 }
             }
         },
         clear_merge_records() {
             this.merge_entry_records = [];
         },
         clear_merge_authors() {
             this.merge_author_records = [];
         },
         merge_records() {
             const vm = this;
             axios.post('/search/api/merge/entries', this.merge_entry_records)
                  .then(function(res) {
                      if (res.data && res.data.success) {
                          vm.clear_merge_records();
                          vm.getResults();
                          vm.flash_success = "Done!"
                      }
                      else if (res.data)  {
                          vm.flash_error = res.data.error || "Failure merging titles!"
                      }
                      else {
                          vm.flash_error = "Failure merging titles!"
                      }
                  })
                  .catch(function(error) {
                      console.log(error)
                  });
         },
         merge_authors() {
             const vm = this;
             axios.post('/search/api/merge/authors', this.merge_author_records)
                  .then(function(res) {
                      console.log(res);
                      if (res.data && res.data.success) {
                          vm.filters = [];
                          vm.clear_merge_authors();
                          // fetch again the facets, although it will cut them.
                          vm.getResults(1);
                          vm.flash_success = "Done!"
                      }
                      else if (res.data)  {
                          vm.flash_error = res.data.error || "Failure merging authors!"
                      }
                      else {
                          vm.flash_error = "Failure merging authors!"
                      }
                  })
                  .catch(function(error) {
                      console.log(error)
                  });
         },
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
    <h1 class="text-3xl text-center font-semibold m-8">Search results ({{ total_entries }})</h1>
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
                      border-gray-300
                      focus:border-pink-500
                      focus:ring-0
                      rounded-l flex-grow"
               type="text" placeholder="Search" v-model="query"/>
        <button class="rounded-r bg-pink-500
                       hover:bg-pink-700 text-white
                       font-semibold mr-1 py-2 px-6 h-11"
                type="submit">Search</button>
      </div>
    </div>
    <div class="grid gap-2 grid-cols-[300px_auto_300px]">
      <div>
        <div>
          <label class="font-semibold" for="limit-facets">Minimum facets results</label><br>
          <input class="rounded 
                        outline
                        outline-0
                        border-gray-300
                        focus:border-pink-500
                        focus:ring-0
                        rounded-l" id="limit-facets" type="number" v-model="limit_facets">
        </div>
        <div v-for="facetblock in facets" :key="facetblock.name" class="mt-3">
          <h2 class="font-semibold capitalize mb-1">{{ facetblock.name }}</h2>
          <template v-for="facet in facetblock.values.filter((el) => el.count > (limit_facets || 0))" :key="facet.key">
            <Facet :term="facet.term" :count="facet.count" :active="facet.active" :name="facetblock.name"
           @toggle-filter="toggleFilter"
            />
          </template>
        </div>
      </div>
      <div>
        <Pagination :pager="pager" @get-page="getPage" />
        <div class="mb-2">
          <template v-for="match in matches" :key="match.entry_id">
            <Entry :record="match" />
          </template>
        </div>
        <Pagination :pager="pager" @get-page="getPage" />
      </div>
      <div v-if="is_authenticated">
        <div class="sticky top-10">
          <div id="author-cards" class="mb-2">
            <div @drop="onAuthorDrop($event)" @dragover.prevent @dragenter.prevent>
              <div class="bg-gray-200 font-semibold 
                          rounded-t border-t border-s border-e border-gray-300 p-2 -space-y-px">
                <h5>Drop authors here for merging</h5>
              </div>
              <div class="rounded-b border border-gray-300">
                <ul role="list">
                  <li class="border-b p-2 font-serif text-sm"
                      v-for="author in merge_author_records">
                    {{ author }}
                  </li>
                </ul>
                <div class="flex justify-center items-center m-2">
                  <div class="px-2">
                    <button class="bg-pink-500 hover:bg-pink-700 text-white font-semibold rounded px-2 py-1 text-sm"
                            type="button" @click="merge_authors">Merge</button>
                  </div>
                  <div class="px-2">
                    <button class="bg-pink-500 hover:bg-pink-700 text-white font-semibold rounded px-2 py-1 text-sm"
                            type="button" @click="clear_merge_authors">Clear</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div id="title-cards">
            <div @drop="onEntryDrop($event)" @dragover.prevent @dragenter.prevent>
              <div class="bg-gray-200 font-semibold 
                          rounded-t border-t border-s border-e border-gray-300 p-2 -space-y-px">
                <h5>Drop titles here for merging</h5>
              </div>
              <div class="rounded-b border border-gray-300">
                <ul role="list">
                  <li class="border-b p-2 font-serif text-sm"
                      v-for="rec in merge_entry_records" :key="rec.entry_id">
                    {{ rec.title }}
                  </li>
                </ul>
                <div class="flex justify-center items-center m-2">
                  <div class="px-2">
                    <button class="bg-pink-500 hover:bg-pink-700 text-white font-semibold rounded px-2 py-1 text-sm"
                            type="button" @click="merge_records">Merge</button>
                  </div>
                  <div class="px-2">
                    <button class="bg-pink-500 hover:bg-pink-700 text-white font-semibold rounded px-2 py-1 text-sm"
                            type="button" @click="clear_merge_records">Clear</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </form>
</template>

