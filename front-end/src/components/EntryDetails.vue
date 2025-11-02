<script>
  export default {
      props: [ 'record' ],
  }
</script>
<template>
  <h2><slot></slot></h2>
  <div v-if="record.authors" class="border-old-copper-100 flex flex-wrap">
    <div v-for="author in record.authors" :key="author.id"
         class="me-2 my-1 p-1 border border-old-copper-200 rounded hover:bg-perl-bush-50">
      <a :href="`/library/author/${author.id}`" class="">
        {{ author.value }}
      </a>
    </div>
  </div>
  <div class="mb-4">
    <div class="flex mt-4 text-lg">
      <h3 class="font-semibold mr-1" v-if="record.title">
        {{ record.title }}
      </h3>
      <div v-if="record.languages">
        <div v-for="l in record.languages" :key="l.id">
          ({{ l.value }})
        </div>
      </div>
    </div>
    <h4 class="italic" v-if="record.subtitle">
      {{ record.subtitle }}
    </h4>
  </div>
</template>
