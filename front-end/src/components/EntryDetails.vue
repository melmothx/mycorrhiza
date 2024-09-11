<script>
  export default {
      props: [ 'record' ],
  }
</script>
<template>
  <h2><slot></slot></h2>
  <div v-if="record.authors">
    <div v-for="author in record.authors" :key="author.id">
      <a :href="`/library/author/${author.id}`">
        {{ author.value }}
      </a>
    </div>
  </div>
  <div class="flex">
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
</template>
