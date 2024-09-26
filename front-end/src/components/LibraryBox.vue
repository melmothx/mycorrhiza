<script>
 import { LinkIcon } from '@heroicons/vue/24/solid'
 export default {
     components: { LinkIcon },
     props: [ "library", "full" ],
 }
</script>
<template>
  <div class="border border-perl-bush-200 bg-perl-bush-50 shadow
              max-w-prose mx-auto
              rounded p-4" v-if="library">
    <slot>
      <h1 class="font-bold text-xl mb-2">{{ library.name }}</h1>
    </slot>
    <div class="my-1" v-if="library.url">
      <a class="text-claret-900 font-bold hover:text-claret-700"
         target="_blank"
         :title="$gettext('Visit Library Homepage')"
         :href="library.url">
        {{ library.url }}
      </a>
    </div>
    <div v-if="library.logo_url">
      <img class="py-1 max-h-64" :src="library.logo_url" :alt="$gettext('%1 logo', library.name)" />
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
      <div class="my-4">
        <router-link class="btn-primary p-1" :to="{ name: 'library_view', params: { id: library.id } }">
          {{ $gettext('Library details') }}
        </router-link>
      </div>
    </div>
    <div class="my-4">
      <a class="btn-primary p-1"
         :href="`/library/entries/${library.id}`">
        {{ $gettext('See the library entries') }}
      </a>
    </div>
  </div>
</template>
  
