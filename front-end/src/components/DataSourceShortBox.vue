<script>
 export default {
     props: [ 'source' ]
 }
</script>
<template>
  <div v-if="source.authors && source.authors.length" class="border-old-copper-100 flex flex-wrap">
    <div v-for="author in source.authors" :key="author" class="me-2 my-2 p-1 border border-old-copper-200 rounded">
      {{ author }}
    </div>
  </div>
  <div class="flex">
    <div class="grow">
      <h3 class="font-semibold mr-1 p-1 grow" v-if="source.title">
        {{ source.title }}
      </h3>
      <h4 class="mr-1 p-1 grow" v-if="source.subtitle">
        <em>{{ source.subtitle }}</em>
      </h4>
    </div>
    <div class="font-bold" v-if="source.languages">
      <span class="bg-linear-to-tr from-spectra-700 to-spectra-900 rounded-sm p-1 shadow-md ml-2 text-white"
            v-for="lang in source.languages" :key="lang">
        {{ lang }}
      </span>
    </div>
  </div>
</template>
