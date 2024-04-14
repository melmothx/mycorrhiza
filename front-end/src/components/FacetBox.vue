<script>
 import FacetButton from './FacetButton.vue'
 import ExclusionButton from './ExclusionButton.vue'
 import { HandRaisedIcon } from '@heroicons/vue/24/solid'
 export default {
      components: { FacetButton, ExclusionButton, HandRaisedIcon },
      props: [ 'name', 'values', 'can_set_exclusions', 'use_sorting', 'translate_values', 'can_merge' ],
      emits: [ 'toggleAppFilter', 'refetchResults' ],
      data() {
          return {
              limit_facets: null,
              sort_method: "count",
          }
      },
      methods: {
          toggleFilter(id, checked) {
              console.log(`Relaying ${this.name} ${id} ${checked}`);
              this.$emit('toggleAppFilter', this.name, id, checked);
          },
          refetchResults() {
              console.log("Relaying refetch results")
              this.$emit('refetchResults');
          },
          drag_element(e, id, label, merge_type) {
              e.dataTransfer.dropEffect = 'copy';
              e.dataTransfer.effectAllowed = 'copy';
              e.dataTransfer.setData('ID', id);
              e.dataTransfer.setData('Label', label);
              e.dataTransfer.setData('Merge', merge_type);
          },
      },
      computed: {
          facet_list() {
              let sort = this.sort_method || "count";
              return this.values
                         .filter((el) => el.count > (this.limit_facets || 0))
                         .sort((a, b) => {
                             if (sort === "term") {
                                 return a.term.localeCompare(b.term);
                             }
                             else {
                                 return b.count - a.count;
                             }
                         });
          },
      }
  }
</script>
<template>
  <div>
    <div class="bg-gradient-to-tr from-old-copper-800 to-old-copper-700 font-semibold rounded-tl-3xl p-2">
      <h2 class="font-semibold capitalize py-0 text-right text-white p-2">
        <slot>{{ name }}</slot>
      </h2>
    </div>
    <div v-if="use_sorting"
         class="bg-gradient-to-tr from-old-copper-300 to-old-copper-200 text-sm px-2 py-2 text-center">
      {{ $gettext('Sort') }}
      <label class="px-2">
        <input class="mcrz-radio"
               type="radio" value="count" v-model="sort_method">
        {{ $gettext('0-9') }}
      </label>
      <label class="px-2">
        <input class="mcrz-radio"
               type="radio" value="term" v-model="sort_method">
        {{ $gettext('A-Z') }}
      </label>
    </div>
    <div class="max-h-48 overflow-y-auto p-2 bg-perl-bush-50">
      <template v-for="facet in facet_list" :key="facet.key">
        <div class="flex">
          <div class="flex-grow">
            <FacetButton
                :id="facet.id"
                :term="facet.term"
                :count="facet.count"
                :active="facet.active"
                :name="name"
                :translate_value="translate_values"
                @toggle-filter="toggleFilter"
            />
          </div>
          <div v-if="can_merge && name == 'creator'">
            <span class="cursor-grab active:cursor-grabbing
                         text-spectra-600 hover:text-spectra-800 hover:text-spectra-800
                         focus:text-spectra-800"
                  draggable="true"
                  @dragstart="drag_element($event, facet.id, facet.term, 'author')">
              <HandRaisedIcon class="h-4 w-4 m-1" />
            </span>
          </div>
          <div class="ml-1" v-if="can_set_exclusions && name == 'library'">
            <ExclusionButton :object_id="facet.id"
                             :object_type="name"
                             @refetch-results="refetchResults">
              {{ $gettext('Omit Library') }}
            </ExclusionButton>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
<style scoped>
</style>
