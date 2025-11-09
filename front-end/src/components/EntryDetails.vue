<script>
  export default {
      props: [ 'record' ],
  }
</script>
<template>
  <div class="mb-4 pb-2">
    <div class="mb-2">
      <h3 class="font-semibold mt-1 text-lg">
        {{ record.title }}
        <span v-if="record.languages">
          <span v-for="l in record.languages" :key="l.id">
            ({{ l.value }})
          </span>
        </span>
      </h3>
      <h4 class="italic" v-if="record.subtitle">
        {{ record.subtitle }}
      </h4>
    </div>
    <div v-if="record.authors" class="border-old-copper-100 flex flex-wrap">
      <div v-for="author in record.authors" :key="author.id"
           class="me-2 my-1 p-1 border border-old-copper-200 rounded hover:bg-perl-bush-50">
        <a :href="`/library/author/${author.id}`" class="">
          {{ author.value }}
        </a>
      </div>
    </div>
  </div>
</template>
