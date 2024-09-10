<script>
 export default {
     props: [ "library", "full" ],
 }
</script>
<template>
  <div v-if="library">
    <slot>
      <h1 class="font-bold text-xl mb-2">{{ library.name }}</h1>
    </slot>
    <div v-if="library.url">
      <a class="text-claret-900 font-bold hover:underline"
         target="_blank"
         :href="library.url">
        {{ $gettext('Visit Library Homepage') }}
      </a>
    </div>
    <div>
      <a class="text-claret-900 font-bold hover:underline"
         :href="`/library/entries/${library.id}`">
        {{ $gettext('See all entries') }}
      </a>
    </div>
    <div v-if="full">
      <div v-if="library.opening_hours">
        <h2 class="font-bold">{{ $gettext('Opening Hours') }}</h2>
        <div>
          {{ library.opening_hours }}
        </div>
      </div>
      <div class="my-5">
        <router-link class="text-claret-900 font-bold hover:underline"
                     :to="{ name: 'library_overview' }">
          {{ $gettext('See all libraries') }}
        </router-link>
      </div>
    </div>
  </div>
</template>
  
