<script>
 export default {
     props: [ 'record' ]
 }
</script>
<template>
  <div v-if="record.authors && record.authors.length" class="border-old-copper-100 flex flex-wrap">
    <a v-for="author in record.authors" :key="author.id"
       :href="`/library/author/${author.id}`"
       class="me-2 my-1 p-1 border border-old-copper-200 rounded hover:bg-perl-bush-50">
      {{ author.value }}
    </a>
  </div>
  <router-link :to="{ name: 'entry', params: { id: record.entry_id } }">
    <div class="flex">
      <div class="grow">
        <h3 v-if="record.title" class="font-semibold">
          {{ record.title }}
        </h3>
        <h4 class="italic" v-if="record.subtitle">
          {{ record.subtitle }}
        </h4>
      </div>
      <div class="font-bold" v-if="record.languages">
        <span class="bg-linear-to-tr from-spectra-700 to-spectra-900 rounded-sm p-1 shadow-md ml-2 text-white"
              v-for="lang in record.languages" :key="lang.id">
          {{ lang.value }}
        </span>
      </div>
    </div>
  </router-link>
</template>
