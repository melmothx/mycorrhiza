<script>
 export default {
     props: ['modelValue'],
     emits: ['update:modelValue'],
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
                    class="absolute inset-y-0 right-0 flex items-center pr-3 font-bold
                          text-claret-800 hover:text-claret-600 cursor-pointer">
              &#10005;
            </button>
          </div>
        </div>
        <button class="btn-primary rounded-none h-10 px-4 w-auto rounded-br-3xl pr-10 pl-4"
                type="submit">
          {{ $gettext('Search') }}
        </button>
      </div>
    </div>
  </form>
</template>
