<script>
 import { QuestionMarkCircleIcon } from '@heroicons/vue/24/solid'
 export default {
     components: {
         QuestionMarkCircleIcon,
     },
     data() {
         return {
             open: false,
         }
     },
     methods: {
         toggle_dialog() {
             this.open = !this.open;
         },
         close_dialog() {
             this.comment = "";
             this.open = false;
         }
     }
 }
</script>
<template>
  <span class="cursor-pointer hover:text-spectra-200 text-lg"
        :title="$gettext('Help')"
        @click="toggle_dialog">
    <QuestionMarkCircleIcon class="w-4 h-4 m-1 hover:text-spectra-200" />
  </span>
  <div v-if="open">
    <div class="fixed inset-x-0 top-0 overflow-y-auto font-normal">
      <div class="flex items-center justify-center p-4">
        <div class="m-8 p-8 w-1/2 border text-black shadow-lg bg-perl-bush-100 shadow-md">
          <div class="px-4 pb-4 pt-5">
            <slot></slot>
          </div>
          <div class="text-center">
            <button class="btn-primary p-2 rounded" @click="close_dialog">
              {{ $gettext('Close') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
