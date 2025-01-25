<script>
 export default {
     props: [ 'active' ],
 }
</script>
<template>
  <div class="text-center text-gray-500">
    <ul class="flex flex-wrap">
      <li>
        <router-link :to="{name: 'bookbuilder'}" :class="active == 'bookbuilder' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          {{ $gettext('Book Builder') }}
        </router-link>
      </li>
      <li>
        <router-link :to="{name: 'coverbuilder'}" :class="active == 'coverbuilder' ? 'mcrz-tab-active' : 'mcrz-tab-normal'">
          {{ $gettext('Covers') }}
        </router-link>
      </li>
    </ul>
  </div>
</template>
