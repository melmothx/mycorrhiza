<script>
 import axios from 'axios'
 import MergeBox from './MergeBox.vue'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     components: {
         MergeBox,
     },
     props: {
         entry_id: {
             type: [String, Number],
             required: true,
         },
         library_id: {
             type: [String, Number],
             required: true,
         }
     },
     data() {
         return {
             entry: {},
             merge_candidates: [],
             loading: false,
             error: null,
             merge_type: 'entry',
         }
     },
     methods: {
         fetch_entry_details() {
             this.loading = true;
             this.error = null;
             axios.get(`/collector/api/entry/${this.entry_id}`)
                  .then(res => {
                      this.entry = res.data;
                      this.fetch_merge_candidates();
                      this.loading = false;
                  })
                  .catch(error => {
                      console.log(error);
                      this.error = "Failed to fetch entry details";
                      this.loading = false;
                  });
         },
         fetch_merge_candidates() {
             axios.get(`/collector/api/entry/${this.entry_id}/merge-candidates`)
                  .then(res => {
                      if (res.data && res.data.candidates) {
                          this.merge_candidates = res.data.candidates;
                      }
                  })
                  .catch(error => {
                      console.log(error);
                  });
         },
         go_back() {
             this.$router.push({ 
                 name: 'merging-support', 
                 params: { library_id: this.library_id } 
             });
         }
     },
     mounted() {
         this.fetch_entry_details();
     }
 }
</script>
<template>
  <div class="m-5 p-4">
    <button @click="go_back" class="btn-primary mb-4 px-4 py-2 rounded font-bold">
      {{ $gettext('Back') }}
    </button>

    <div v-if="loading" class="text-center py-8">
      <span class="animate-ping text-spectra-700">{{ $gettext('Loading...') }}</span>
    </div>
    <div v-else-if="error" class="text-claret-900 font-bold py-4 bg-red-100 border border-red-300 rounded p-3 mb-4">
      {{ $gettext(error) }}
    </div>
    <div v-if="!loading" class="space-y-6">
      <!-- Primary Entry -->
      <div class="border rounded-lg shadow-md p-4 bg-gradient-to-r from-spectra-50 to-spectra-100">
        <h2 class="text-xl font-bold text-spectra-900 mb-2">{{ entry.title }}</h2>
        <div class="text-gray-700 font-semibold">{{ entry.authors }}</div>
        <div v-if="entry.year_edition" class="text-sm text-gray-600 mt-2">
          {{ $gettext('Year') }}: {{ entry.year_edition }}
        </div>
      </div>

      <!-- Merge Candidates -->
      <div v-if="merge_candidates.length > 0">
        <h3 class="text-lg font-bold text-claret-900 mb-4">
          {{ $gettext('Possible Duplicates (%1)', merge_candidates.length) }}
        </h3>
        <MergeBox :merge_type="merge_type"
                  :api_call="`merge/${entry.id}`"
                  @refetchResults="fetch_merge_candidates" />
      </div>
      <div v-else class="text-center py-8 text-gray-500 bg-gray-50 rounded border">
        {{ $gettext('No merge candidates found') }}
      </div>
    </div>
  </div>
</template>
