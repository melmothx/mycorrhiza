<script>
  export default {
      props: ['term', 'count', 'active', 'name'],
      emits: ['toggleFilter'],
  }
</script>
<template>
  <div class="font-serif">
    <label>
      <input type="checkbox" class="rounded focus:border-pink-500 text-pink-500 focus:ring-0"
             :checked="active"
             @change="$emit('toggleFilter', term, name , $event.target.checked)" />
      {{ term }} ({{ count }})
    </label>
  </div>
</template>
<style scoped>
</style>
