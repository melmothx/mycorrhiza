<script>
 import FacetButton from './FacetButton.vue'
  export default {
      components: { FacetButton },
      props: [ 'name', 'values' ],
      emits: [ 'toggleAppFilter' ],
      data() {
          return {
              limit_facets: 0,
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
  <h2 class="font-semibold capitalize">{{ name }}</h2>
  <div class="h-48 overflow-y-auto">
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
</template>
<style scoped>
</style>
