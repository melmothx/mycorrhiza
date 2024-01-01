<script>
  export default {
      props: [ 'record' ],
  }
</script>
<template>
  <h3><slot></slot></h3>
  <div v-if="record.authors">
    <div v-for="author in record.authors" :key="author.id">
      {{ author.value }}
    </div>
  </div>
  <strong v-if="record.title">
    {{ record.title }}
  </strong>
  <strong v-if="record.subtitle">
    {{ record.subtitle }}
  </strong>
  <span v-if="record.year_edition">
    ({{ record.year_edition }})
  </span>
  <span v-if="record.year_first_edition">
    (First edition: {{ record.year_first_edition }})
  </span>
  <p v-if="record.description">{{ record.description }}</p>
</template>
