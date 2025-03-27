<script>
 import { QuestionMarkCircleIcon } from '@heroicons/vue/24/solid'
 export default {
     props: [
         'container_class',
         'icon_class',
     ],
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
  <span :class="container_class"
        :title="$gettext('Help')"
        @click="toggle_dialog">
    <QuestionMarkCircleIcon :class="icon_class" />
  </span>
  <div v-if="open">
    <div class="fixed inset-x-0 top-0 overflow-y-auto font-normal">
      <div class="flex items-center justify-center p-4">
        <div class="m-8 p-8 w-1/2 border text-black shadow-lg bg-perl-bush-100 shadow-md">
          <div class="px-4 pb-4 pt-5">
            <slot></slot>
          </div>
          <div class="text-center">
            <button class="btn-primary p-2 rounded-sm" @click="close_dialog">
              {{ $gettext('Close') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
