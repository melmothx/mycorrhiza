<script>
 import { LinkIcon } from '@heroicons/vue/24/solid';
 import LibraryLink from './LibraryLink.vue';
 export default {
     components: {
         LinkIcon,
         LibraryLink,
     },
     props: [ "library", "full", "short" ],
 }
</script>
<template>
  <div class="mcrz-text-box" v-if="library">
    <div v-if="library.logo_url">
      <img class="py-1 max-h-12 mx-auto mb-2"
           :src="library.logo_url" :alt="$gettext('%1 logo', library.name)" />
    </div>
    <slot>
      <h1 class="font-bold">{{ library.name }}</h1>
    </slot>
    <LibraryLink :url="library.url" class="my-1" />
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
        <h2 class="mt-2 font-bold">{{ $gettext('Opening Hours') }}</h2>
        <p class="whitespace-pre-line">
          {{ library.opening_hours }}
        </p>
      </div>
      <div v-if="library.email_public" class="my-2">
        <strong class="font-bold pr-2">{{ $gettext('Email:') }}</strong>
        <a :href="`mailto:${library.email_public}`">
          <span class="font-mono">{{ library.email_public }}</span>
        </a>
      </div>
      <div v-if="library.address_line_1 || library.address_zip || library.address_city || library.country">
        <h2 class="mt-2 font-bold">{{ $gettext('Address') }}</h2>
        <div v-if="library.address_line_1">
          {{ library.address_line_1 }}
        </div>
        <div v-if="library.address_line_2">
          {{ library.address_line_2 }}
        </div>
        <div>
          {{ library.address_zip }}
          {{ library.address_city }}
          {{ library.address_country }}
        </div>
      </div>
      <div v-if="library.pgp_public_key">
        <h2 class="mt-2 font-bold">{{ $gettext('PGP Public Key') }}</h2>
        <pre class="text-[12px] border p-1">{{ library.pgp_public_key }}</pre>
      </div>
    </div>
    <div v-else>
      <div class="my-2" v-if="library.short_desc">
        <p class="whitespace-pre-line">
          {{ library.short_desc }}
        </p>
      </div>
      <router-link :to="{ name: 'library_view', params: { id: library.id } }">
        <div class="my-4 text-sm btn-primary py-1 px-2 rounded">
          {{ $gettext('Library details') }}
        </div>
      </router-link>
    </div>
    <a :href="`/library/entries/${library.id}`">
      <div v-if="!short && library.catalog_is_accessible"
           class="my-4 text-sm btn-primary py-1 px-2 rounded">
        {{ $gettext('See the library entries') }}
      </div>
    </a>
  </div>
</template>
  
