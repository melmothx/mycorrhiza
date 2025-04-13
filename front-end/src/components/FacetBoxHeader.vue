<script>
 import { ListBulletIcon } from '@heroicons/vue/24/solid'
 export default {
     props: [ 'link_name', 'title' ],
     components:  {
         ListBulletIcon,
     }           
 }
</script>
<template>
  <div class="bg-linear-to-tr from-old-copper-800 to-old-copper-700 font-semibold rounded-tl-3xl">
    <h2 class="font-semibold capitalize py-2 text-right text-white px-2 text-sm">
      <template v-if="link_name">
        <router-link :to="{ name: link_name }" class="hover:underline flex">
          <span class="grow"></span>
          {{ title }}
          <ListBulletIcon class="h-4 w-4 ml-1 mt-px" />
        </router-link>
      </template>
      <template v-else>
        {{ title }}
      </template>
    </h2>
  </div>
</template>
