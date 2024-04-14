<script>
  export default {
      props: ['id', 'term', 'count', 'active', 'name', 'merge_type', 'translate_value'],
      emits: ['toggleFilter'],
      methods: {
      },
  }
</script>
<template>
  <div class="font-serif">
    <label>
      <input type="checkbox" class="mcrz-checkbox"
             :checked="active"
             @change="$emit('toggleFilter', id , $event.target.checked)" />
      <span class="ml-1">
        <template v-if="translate_value">
          {{ $gettext(term) }}
        </template>
        <template v-else>
          {{ term }}
        </template>
      </span>
      ({{ count }})
    </label>
  </div>
</template>
<style scoped>
</style>
