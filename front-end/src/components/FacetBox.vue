<script>
 import FacetButton from './FacetButton.vue'
  export default {
      components: { FacetButton },
      props: [ 'name', 'values' ],
      emits: [ 'toggleAppFilter' ],
      data() {
          return {
              limit_facets: null,
          }
      },
      methods: {
          toggleFilter(id, checked) {
              console.log(`Relaying ${this.name} ${id} ${checked}`);
              this.$emit('toggleAppFilter', this.name, id, checked);
          },
      },
  }
</script>
<template>
  <div class="rounded-lg p-0 border border-gray-300">
    <div class="flex justify-center align-center border-b p-2 bg-gray-100 rounded-t-lg">
      <h2 class="font-semibold flex-grow capitalize py-2">
        <slot>{{ name }}</slot>
      </h2>
      <input type="number" v-model="limit_facets"
             size="4" min="0" step="1"
             title="Minimum number of results"
             class="rounded
                   border
                   text-sm
                   border-gray-300
                   outline
                   outline-0
                   focus:border-pink-500
                   focus:ring-0
                   px-1 py-0 m-0" />
    </div>
    <div class="h-48 overflow-y-auto p-2">
      <template v-for="facet in values.filter((el) => el.count > (limit_facets || 0))"
                :key="facet.key">
        <FacetButton
            :id="facet.id"
            :term="facet.term"
            :count="facet.count"
            :active="facet.active"
            :name="name"
            :merge_type="name == 'creator' ? 'author' : ''"
            @toggle-filter="toggleFilter"
        />
      </template>
    </div>
  </div>
</template>
<style scoped>
</style>