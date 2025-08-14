<script>
 import SearchHelp from './SearchHelp.vue'
 export default {
     components: {
         SearchHelp,
     },
     props: ['modelValue'],
     emits: ['update:modelValue'],
     data() {
         return { show_query_help: false, };
     },
     computed: {
         value: {
             get() {
                 return this.modelValue
             },
             set(value) {
                 this.$emit('update:modelValue', value)
             }
         },
     }
 }
</script>
<template>
  <form action="/search" method="GET">
    <div>
      <div class="w-full flex flex-nowrap">
        <div class="w-full flex-grow">
          <div class="relative flex">
            <input class="mcrz-input shadow-sm h-10 rounded-4 flex-grow"
                   name="query"
                   v-model="value"
                   type="text" :placeholder="$gettext('Search')"/>
            <button v-if="value" type="button"
                    @click="value = ''"
                    class="absolute inset-y-0 right-2 font-bold
                          w-4 px-4
                          text-claret-800 hover:text-claret-600 cursor-pointer">
              &#10005;
            </button>
            <button v-if="value" type="button"
                    :title="$gettext('Help on the query syntax')"
                    @click="show_query_help = show_query_help ? false : true"
                    class="absolute inset-y-0 right-8 font-bold
                          w-4 px-4
                          text-spectra-600 hover:text-spectra-500 cursor-pointer">
            ?
          </button>
          </div>
        </div>
        <button class="btn-primary rounded-none h-10 px-4 w-auto rounded-br-3xl pr-10 pl-4"
                type="submit">
          {{ $gettext('Search') }}
        </button>
      </div>
    </div>
    <SearchHelp v-if="show_query_help" />
  </form>
</template>
