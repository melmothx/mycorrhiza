<script>
 export default {
     props: ['pager'],
     emits: ['getPage'],
 }
</script>
<template>
  <nav class="inline-flex text-sm">
    <template v-for="page in pager" :key="page.key">
      <a class="flex font-sans items-center justify-center mr-1 px-4 h-8
                last:rounded-br-3xl
                last:pr-10
                hover:bg-cedar-800
                bg-cedar-950"
         href="#" @click="$emit('getPage', page.page_id)">
        <span v-if="page.current" class="text-white font-bold">
          {{ page.label }}
        </span>
        <span v-else class="text-white">
          {{ page.label }}
        </span>
      </a>
    </template>
  </nav>
</template>
<style scoped>
</style>
