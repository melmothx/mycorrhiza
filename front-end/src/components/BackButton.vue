<script>
 export default {
     methods: {
         has_history() {
             if (window.history.length > 2) {
                 return true;
             }
             else {
                 return false;
             }
         },
     }
 }
</script>
<template>
  <button class="btn-primary rounded-br-3xl h-8 pr-10 pl-4 pr-10"
          type="button"
          @click="has_history() ? $router.go(-1) : $router.push({ 'name': 'home' })">
    {{ $gettext('Back') }}
  </button>
</template>
