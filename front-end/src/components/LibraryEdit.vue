<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import HelpPopUp from './HelpPopUp.vue'
 export default {
     props: [ 'library_id' ],
     components: { HelpPopUp },
     data() {
         return {
             library: {},
             error: null,
             success: null,
             users: [],
         }
     },
     methods: {
         reset_messages() {
             this.error = null;
             this.success = null;
         },
         fetch() {
             axios.get('/collector/api/library/details/' + this.library_id)
                  .then(res => {
                      console.log(res.data);
                      this.error = res.data.error;
                      if (res.data.library) {
                          this.library = res.data.library;
                          this.users = res.data.users || [];
                      }
                  })
                  .catch(error => {
                      this.error = error;
                  });
         },
         update() {
             this.reset_messages();
             axios.post('/collector/api/library/details/' + this.library_id,
                        this.library)
                  .then(res => {
                      this.error = res.data.error;
                      this.success = "The library was updated";
                      if (!this.error) {
                          this.fetch();
                      }
                  })
                  .catch(error => {
                      this.error = error;
                  });
         },
     },
     mounted() {
         this.reset_messages();
         this.fetch();
     }
 }
</script>
<template>
  <div>
    <div v-if="error" class="py-2 text-claret-900 font-bold">
      {{ $gettext(error) }}
    </div>
    <div v-if="success" class="py-2 text-spectra-800 font-bold">
      {{ $gettext(success) }}
    </div>
    <div>
      <div>
        <router-link :to="{ name: 'library_view', params: { id: library.id } }">
          <h1 class="font-bold text-claret-900 text-xl">{{ library.name }}</h1>
        </router-link>
        <form @submit.prevent="update">
          <div>
            <label for="library-url">{{ $gettext('Internet address') }}</label>
            <div class="flex">
              <input class="mcrz-input" id="library-url" v-model="library.url" />
            </div>
          </div>
          <div>
            <div class="flex">
              <label class="grow" for="library-logo-url">{{ $gettext('Logo URL') }}</label>
              <HelpPopUp container_class="cursor-pointer"
                         icon_class="w-4 h-4 m-1 text-spectra-900 hover:text-spectra-700">
                {{ $gettext('Logo address, e.g. https://mydomain.org/path/to/image') }}
              </HelpPopUp>
            </div>

            <div class="flex">
              <input class="mcrz-input" id="library-logo-url" v-model="library.logo_url" />
            </div>
          </div>
          <div>
            <label for="email-public">{{ $gettext('Public email') }}</label>
            <div class="flex">
              <input class="mcrz-input" type="email" id="email-public" v-model="library.email_public" />
            </div>
          </div>
          <div>
            <label for="email-internal">{{ $gettext('Internal email') }}</label>
            <div class="flex">
              <input class="mcrz-input" type="email" id="email-internal" v-model="library.email_internal"
                     required/>
            </div>
          </div>
          <div>
            <label for="opening_hours">{{ $gettext('Opening Hours') }}</label>
            <div class="flex">
              <textarea class="mcrz-input" id="opening_hours" v-model="library.opening_hours"></textarea>
            </div>
          </div>
          <div>
            <div class="flex">
              <label class="grow" for="short_desc">{{ $gettext('Short Description') }}</label>
              <HelpPopUp container_class="cursor-pointer"
                         icon_class="w-4 h-4 m-1 text-spectra-900 hover:text-spectra-700">
                {{ $gettext('Please describe the project. Just a few words, for the preview') }}
              </HelpPopUp>
            </div>
            <div class="flex">
              <textarea class="mcrz-input" id="short_desc" v-model="library.short_desc"></textarea>
            </div>
          </div>
          <div>
            <div class="flex">
              <label class="grow" for="description">{{ $gettext('Description') }}</label>
              <HelpPopUp container_class="cursor-pointer"
                         icon_class="w-4 h-4 m-1 text-spectra-900 hover:text-spectra-700">
                {{ $gettext('This is a free-text field. Please describe the project') }}
              </HelpPopUp>
            </div>
            <div class="flex">
              <textarea class="mcrz-input" id="description" v-model="library.description"></textarea>
            </div>
          </div>
          <div>
            <div class="flex">
              <label class="grow" for="languages">{{ $gettext('Languages') }}</label>
              <HelpPopUp container_class="cursor-pointer"
                         icon_class="w-4 h-4 m-1 text-spectra-900 hover:text-spectra-700">
                {{ $gettext('This is a free-text field. Please explain briefly which are the project languages') }}
              </HelpPopUp>
            </div>
            <div class="flex">
              <textarea class="mcrz-input" id="languages" v-model="library.languages"></textarea>
            </div>
          </div>
          <div>
            <div class="flex">
              <label class="grow" for="pgp_public_key">{{ $gettext('PGP public key, if any') }}</label>
            </div>
            <div class="flex">
              <textarea class="mcrz-input font-mono text-sm" id="pgp_public_key"
                        v-model="library.pgp_public_key"></textarea>
            </div>
          </div>

          <div>
            <div class="flex">
              <label class="grow" for="address_line_1">{{ $gettext('Address Line') }}</label>
            </div>
            <div class="flex">
              <input class="mcrz-input" id="address_line_1" v-model="library.address_line_1" />
            </div>
          </div>
          <div>
            <div class="flex">
              <label class="grow" for="address_line_2">{{ $gettext('Additional Address Line') }}</label>
            </div>
            <div class="flex">
              <input class="mcrz-input" id="address_line_2" v-model="library.address_line_2" />
            </div>
          </div>

          <div>
            <div class="flex">
              <label class="grow" for="address_zip">{{ $gettext('ZIP code') }}</label>
            </div>
            <div class="flex">
              <input class="mcrz-input" id="address_zip" v-model="library.address_zip" />
            </div>
          </div>
          <div>
            <div class="flex">
              <label class="grow" for="address_city">{{ $gettext('City') }}</label>
            </div>
            <div class="flex">
              <input class="mcrz-input" id="address_city" v-model="library.address_city" />
            </div>
          </div>
          <div>
            <div class="flex">
              <label class="grow" for="address_state">{{ $gettext('State or Province') }}</label>
            </div>
            <div class="flex">
              <input class="mcrz-input" id="address_state" v-model="library.address_state" />
            </div>
          </div>
          <div>
            <div class="flex">
              <label class="grow" for="address_country">{{ $gettext('Country') }}</label>
            </div>
            <div class="flex">
              <input class="mcrz-input" id="address_country" v-model="library.address_country" />
            </div>
          </div>
          <div>
            <label for="year_established">{{ $gettext('Date Established') }}</label>
            <div class="flex">
              <input class="mcrz-input" type="date" v-model="library.year_established" />
            </div>
          </div>
          <div>
            <label for="latitude">{{ $gettext('Latitude') }}</label>
            <div class="flex">
              <input class="mcrz-input" type="number" min="-90" max="90" step="0.000001" id="latitude" v-model="library.latitude" />
            </div>
          </div>
          <div>
            <label for="longitude">{{ $gettext('Longitude') }}</label>
            <div class="flex">
              <input class="mcrz-input" type="number" min="-180" max="180" step="0.000001" id="longitude" v-model="library.longitude" />
            </div>
          </div>
          <div class="mt-2">
            <button class="btn-primary p-1" type="submit">{{ $gettext('Update') }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
