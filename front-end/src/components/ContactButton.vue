<script>
 export default {
     data() {
         return {}
     }
 }
</script>
<template>
  <router-link :to="{ name: 'contact' }" class="btn-accent text-sm px-4 py-1 rounded-sm shadow-lg">
    <slot>{{ $gettext('Contacts') }}</slot>
  </router-link>
</template>
