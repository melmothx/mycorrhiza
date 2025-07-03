<script>
 export default {
     components: {},
     data() {
         return {}
     }
 }
</script>
<template>
  <form action="/search" method="GET">
    <div>
      <div class="relative w-full">
        <input class="mcrz-input shadow-sm w-full h-12 rounded-4"
               name="query"
               type="text" :placeholder="$gettext('Search')"/>
        <button v-if="query" type="button"
                class="absolute inset-y-0 right-0 flex items-center pr-3 font-bold
                      text-claret-800 hover:text-claret-600 cursor-pointer">
          &#10005;
        </button>
      </div>
    </div>
  </form>
</template>
