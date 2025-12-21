<script>
 export default {
     data() {
         return {}
     }
 }
</script>
<template>
  <router-link :to="{ name: 'contact' }">
    <div class="btn-accent text-sm mx-4 p-2 rounded-sm shadow-lg text-center">
      {{ $gettext('Contacts') }}
    </div>
  </router-link>
</template>
