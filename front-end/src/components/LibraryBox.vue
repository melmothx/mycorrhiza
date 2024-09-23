<script>
 import { LinkIcon } from '@heroicons/vue/24/solid'
 export default {
     components: { LinkIcon },
     props: [ "library", "full" ],
 }
</script>
<template>
  <div v-if="library">
    <slot>
      <h1 class="font-bold text-xl mb-2">{{ library.name }}</h1>
    </slot>
    <div class="my-1" v-if="library.url">
      <a class="text-claret-900 font-bold hover:text-claret-700"
         target="_blank"
         :title="$gettext('Visit Library Homepage')"
         :href="library.url">
        <div>
          {{ library.url }}
        </div>
        <div v-if="library.logo_url">
          <img class="py-1 w-full max-h-40" :src="library.logo_url" :alt="$gettext('%1 logo', library.name)" />
        </div>
      </a>
    </div>
    <div v-if="library.established" class="font-bold my-1">
      {{ $gettext('Project established in %1', library.established) }}
    </div>
    <div v-if="library.languages" class="font-bold my-1">
      {{ library.languages }}
    </div>
    <div v-if="full">
      <div class="my-2" v-if="library.description">
        <p class="whitespace-pre-line">
          {{ library.description }}
        </p>
      </div>
      <div v-if="library.opening_hours">
        <h2 class="font-bold">{{ $gettext('Opening Hours') }}</h2>
        <p class="whitespace-pre-line">
          {{ library.opening_hours }}
        </p>
      </div>
      <div v-if="library.email_public" class="my-1 font-bold">
        {{ $gettext('Email:') }}
        <a :href="`mailto:${library.email_public}`">{{ library.email_public }}</a>
      </div>
    </div>
    <div class="mt-2">
      <a class="btn-primary p-1"
         :href="`/library/entries/${library.id}`">
        {{ $gettext('See the library entries') }}
      </a>
    </div>
  </div>
</template>
  
