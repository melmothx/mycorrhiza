<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import JobChecker from './JobChecker.vue'
 export default {
     components: {
         JobChecker,
     },
     data() {
         return {
             tokens: [],
             fonts: [],
             bookcover: {},
             session_id: null,
             job_id: null,
         }
     },
     methods: {
         get_fonts() {
             axios.post('/collector/api/bookbuilder', { action: "get_fonts" })
                  .then(res => {
                      console.log(res.data);
                      this.fonts = res.data.fonts;
                  });
         },
         get_tokens() {
             axios.post('/collector/api/bookcover',
                        { action: "get_tokens" })
                  .then(res => {
                      this.tokens = res.data.tokens;
                      this.session_id = res.data.session_id;
                      for (const token of this.tokens) {
                          this.bookcover[token.name] = token.value;
                      }
                  });
         },
         load_file(e, token_name) {
             let form_data = new FormData();
             form_data.append(token_name, event.target.files[0]);
             form_data.append('session_id', this.session_id);
             axios.post('/collector/api/bookcover/upload',
                        form_data,
                        { headers: { 'Content-Type': 'multipart/form-data' } })
                  .then(res => {
                      console.log(res.data);
                      for (const tn in res.data.tokens) {
                          this.bookcover[tn] = res.data.tokens[tn]
                      }
                  });
         },
         build_cover() {
             const params = {
                 action: "build",
                 args: this.bookcover,
             };
             params.args.session_id = this.session_id;
             axios.post('/collector/api/bookcover', params)
                  .then(res => {
                      console.log(res.data)
                      this.job_id = res.data.job_id;
                  });
         },
     },
     mounted() {
         this.get_tokens();
         this.get_fonts();
     }
 }
</script>
<template>
  <div class="font-medium text-center text-gray-500 mb-8">
    <ul class="flex flex-wrap">
      <li class="mcrz-tab-normal">
        <router-link :to="{ name: 'bookbuilder' }">
          {{ $gettext('Book Builder') }}
        </router-link>
      </li>
      <li class="mcrz-tab-active">
        {{ $gettext('Covers') }}
      </li>
    </ul>
  </div>
  <div class="grid sm:grid-cols-[auto_300px] gap-6">
    <div>
      <div v-for="token in tokens">
        <div class="grid sm:grid-cols-[150px_auto] gap-4 flex items-center my-4">
          <template v-if="token.type == 'int'">
            <label :for="`bc-${token.name}`" class="font-bold">
              {{ $gettext(token.desc) }}
            </label>
            <div>
              <input class="mcrz-input" type="number" step="1" min="0" v-model="bookcover[token.name]"
                     :id="`bc-${token.name}`">
            </div>
          </template>
          <template v-if="token.type == 'bool'">
            <label for="`bc-${token.name}`" class="font-bold">
              {{ $gettext(token.desc) }}
            </label>
            <div>
              <input id="`bc-${token.name}`"
                     class="mcrz-checkbox" type="checkbox" value="1" v-model="bookcover[token.name]" :id="`bc-${token.name}`" />
            </div>
          </template>
          <template v-if="token.type == 'muse_str'">
            <label :for="`bc-${token.name}`" class="font-bold">
              {{ $gettext(token.desc) }}
            </label>
            <div>
              <input class="mcrz-input w-full" type="text" v-model="bookcover[token.name]"
                     :id="`bc-${token.name}`">
            </div>
          </template>
          <template v-if="token.type == 'muse_body'">
            <label :for="`bc-${token.name}`" class="font-bold">
              {{ $gettext(token.desc) }}
            </label>
            <div class="w-full">
              <textarea class="mcrz-textarea w-full" v-model="bookcover[token.name]"></textarea>
            </div>
          </template>
          <template v-if="token.type == 'file'">
            <label :for="`bc-${token.name}`" class="font-bold">
              {{ $gettext(token.desc) }}
            </label>
            <div>
              <input class="mcrz-input" type="file" @change="load_file($event, token.name)"
                     :id="`bc-${token.name}`">
            </div>
          </template>
          <template v-if="token.type == 'isbn'">
            <label :for="`bc-${token.name}`" class="font-bold">
              {{ $gettext(token.desc) }}
            </label>
            <div>
              <input class="mcrz-input" type="text" v-model="bookcover[token.name]"
                     pattern="\d{10,13}"
                     :id="`bc-${token.name}`">
            </div>
          </template>
          <template v-if="token.type == 'select'">
            <label :for="`bc-${token.name}`" class="font-bold">
              {{ $gettext(token.desc) }}
            </label>
            <div>
              <select class="mcrz-select" v-model="bookcover[token.name]">
                <option v-for="opt in token.options" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
          </template>
        </div>
      </div>
    </div>
    <div>
      <div>
        <img class="w-full" src="/bookcover.png" />
      </div>
      <a class="mcrz-href-primary"
         target="_blank"
         href="http://mirrors.ctan.org/macros/latex/contrib/bookcover/bookcover.pdf">
        {{ $gettext('See the bookcover class for all the details')  }}
      </a>
      <div class="bg-perl-bush-50 p-2 shadow-md rounded">
        <div v-for="font in fonts.filter(f => f.name == bookcover.font_name)">
          <a :href="font.preview_pdf" target="_blank">
            <img class="mx-auto my-4 max-h-96" :src="font.preview_png">
            {{ font.name }}
          </a>
        </div>
      </div>
    </div>
  </div>
  <div class="mt-8 flex">
    <button class="btn-accent m-1 px-4 py-1 rounded shadow-lg" @click="build_cover">
      {{ $gettext('Build') }}
    </button>
  </div>
  <JobChecker :session_id="session_id" :job_id="job_id" :key="job_id" />
</template>
