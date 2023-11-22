<script>
 export default {
     props: ['pager'],
     emits: ['getPage'],
 }
</script>
<template>
  <nav class="inline-flex text-sm -space-x-px">
    <template v-for="page in pager" :key="page.key">
      <template v-if="page.current">
        <a href="#" @click="$emit('getPage', page.page_id)"
           aria-current="page"
           class="flex items-center justify-center mx-0 px-4 h-10 border border-gray-300 
                 bg-pink-500 text-white font-bold
                 first:rounded-l last:rounded-r">
          {{ page.label }}</a>
      </template>
      <template v-else>
        <a class="flex items-center justify-center mx-0 ms-0 px-4 h-10 border border-gray-300 first:rounded-l last:rounded-r"
           href="#" @click="$emit('getPage', page.page_id)">{{ page.label }}</a>
      </template>
    </template>
  </nav>
</template>
<style scoped>
</style>
