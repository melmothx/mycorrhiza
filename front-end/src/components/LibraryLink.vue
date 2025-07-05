<script>
 export default {
     props: [ "url" ],
     methods: {
         bare_url(url) {
             return url.replace(/https?:\/\//, '').replace(/\/$/, '');
         },
     },
 }
</script>
<template>
  <div v-if="url">
    <a class="text-sm text-claret-900 font-bold hover:text-claret-700"
       target="_blank"
       :title="$gettext('Visit Library Homepage')"
       :href="url">
      {{ bare_url(url) }}
    </a>
  </div>
</template>
