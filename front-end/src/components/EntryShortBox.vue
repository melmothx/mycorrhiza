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
        <template v-if="record.title && record.title.length">
          <h3 class="font-semibold mr-1 p-1 grow" v-for="title in record.title">
            {{ title.value }}
          </h3>
        </template>
        <template v-if="record.subtitle && record.subtitle.length">
          <h4 class="mr-1 p-1 grow" v-for="subtitle in record.subtitle">
            <em>{{ subtitle.value }}</em>
          </h4>
        </template>
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
