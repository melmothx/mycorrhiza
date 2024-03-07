<script>
 import FacetButton from './FacetButton.vue'
 import ExclusionButton from './ExclusionButton.vue'
  export default {
      components: { FacetButton, ExclusionButton },
      props: [ 'name', 'values', 'can_set_exclusions', 'use_sorting', 'translate_values' ],
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
          }
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
  <div class="rounded-lg p-0 border border-gray-300">
    <div class="border-b pt-0 bg-gray-100 rounded-t-lg">
      <h2 class="font-semibold capitalize py-0 text-center border-b">
        <slot>{{ name }}</slot>
      </h2>
      <div v-if="use_sorting"
           class="text-sm px-2 py-0 text-center">
        {{ $gettext('Sort') }}
        <label class="px-2">
          <input class="text-pink-500 focus:ring-pink-500 focus:ring-0 active:ring-0"
                 type="radio" value="count" v-model="sort_method">
          {{ $gettext('by count') }}
        </label>
        <label class="px-2">
          <input class="text-pink-500 focus:ring-pink-500 focus:ring-0 active:ring-0"
                 type="radio" value="term" v-model="sort_method">
          {{ $gettext('by term') }}
        </label>
      </div>
    </div>
    <div class="max-h-48 overflow-y-auto p-2">
      <template v-for="facet in facet_list" :key="facet.key">
        <div class="flex">
          <div class="flex-grow">
            <FacetButton
                :id="facet.id"
                :term="facet.term"
                :count="facet.count"
                :active="facet.active"
                :name="name"
                :merge_type="name == 'creator' ? 'author' : ''"
                :translate_value="translate_values"
                @toggle-filter="toggleFilter"
            />
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
