<script>
 export default {
     props: ['pager'],
     emits: ['getPage'],
 }
</script>
<template>
  <nav v-if="pager.length" class="inline-flex text-sm mb-8">
    <template v-for="page in pager" :key="page.key">
      <span class="flex items-center justify-center mr-1
                   cursor-pointer
                   last:rounded-br-3xl
                   last:pr-10
                   hover:bg-cab-sav-800
                   bg-cab-sav-950"
            @click="$emit('getPage', page.page_id)">
        <span v-if="page.current" class=" px-3 py-2 bg-cab-sav-800 text-white font-bold">
          {{ page.label }}
        </span>
        <span v-else class="px-3 py-2 text-white">
          {{ page.label }}
        </span>
      </span>
    </template>
  </nav>
</template>
<style scoped>
</style>
