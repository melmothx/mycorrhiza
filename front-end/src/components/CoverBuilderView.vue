<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     data() {
         return {
             tokens: [],
             bookcover: {},
         }
     },
     methods: {
         get_tokens() {
             axios.post('/collector/api/bookcover',
                        { action: "get_tokens" })
                  .then(res => {
                      this.tokens = res.data.tokens;
                      for (const token of this.tokens) {
                          this.bookcover[token.name] = token.value;
                      }
                  });
         },
         load_file(e) {
         },
     },
     mounted() {
         this.get_tokens();
     }
 }
</script>
<template>
  <div class="font-medium text-center text-gray-500 mb-8">
    <ul class="flex flex-wrap">
      <li class="mcrz-tab-active">
        {{ $gettext('Covers') }}
      </li>
      <li class="mcrz-tab-normal">
        <router-link :to="{ name: 'bookbuilder' }">
          {{ $gettext('Book Builder') }}
        </router-link>
      </li>
    </ul>
  </div>
  <div>
    <div v-for="token in tokens" :key="name">
      <div v-if="token.type == 'int'">
        <div class="grid sm:grid-cols-[150px_auto] gap-4 flex items-center my-4">
          <label :for="`bc-${token.name}`" class="font-bold">
            {{ $gettext(token.desc) }}
          </label>
          <div>
            <input class="mcrz-input" type="number" step="1" min="0" v-model="bookcover[token.name]"
                   :id="`bc-${token.name}`">
          </div>
        </div>
      </div>
      <div v-if="token.type == 'bool'">
        <div class="grid sm:grid-cols-[150px_auto] gap-4 flex items-center my-4">
          <label for="`bc-${token.name}`" class="font-bold">
            {{ $gettext(token.desc) }}
          </label>
          <div>
            <input id="`bc-${token.name}`"
                   class="mcrz-checkbox" type="checkbox" value="1" v-model="bookcover[token.name]" :id="`bc-${token.name}`" />
          </div>
        </div>
      </div>
      <div v-if="token.type == 'muse_str'">
        <div class="grid sm:grid-cols-[150px_auto] gap-4 flex items-center my-4">
          <label :for="`bc-${token.name}`" class="font-bold">
            {{ $gettext(token.desc) }}
          </label>
          <div>
            <input class="mcrz-input w-full" type="text" v-model="bookcover[token.name]"
                   :id="`bc-${token.name}`">
          </div>
        </div>
      </div>
      <div v-if="token.type == 'muse_body'">
        <div class="grid sm:grid-cols-[150px_auto] gap-4 flex items-center my-4">
          <label :for="`bc-${token.name}`" class="font-bold">
            {{ $gettext(token.desc) }}
          </label>
          <div class="w-full">
            <textarea class="mcrz-textarea w-full" v-model="bookcover[token.name]"></textarea>
          </div>
        </div>
      </div>
      <div v-if="token.type == 'file'">
        <div class="grid sm:grid-cols-[150px_auto] gap-4 flex items-center my-4">
          <label :for="`bc-${token.name}`" class="font-bold">
            {{ $gettext(token.desc) }}
          </label>
          <div>
            <input class="mcrz-input" type="file" @change="load_file($event)"
                   :id="`bc-${token.name}`">
          </div>
        </div>
      </div>
      <div v-if="token.type == 'isbn'">
        <div class="grid sm:grid-cols-[150px_auto] gap-4 flex items-center my-4">
          <label :for="`bc-${token.name}`" class="font-bold">
            {{ $gettext(token.desc) }}
          </label>
          <div>
            <input class="mcrz-input" type="text" v-model="bookcover[token.name]"
                   pattern="\d{10,13}"
                   :id="`bc-${token.name}`">
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
