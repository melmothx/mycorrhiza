<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import DashboardTable from './DashboardTable.vue'
 import UserCreation from './UserCreation.vue'
 import CsvUpload from './CsvUpload.vue'
 export default {
     props: [ 'library_id' ],
     components: {
         DashboardTable,
         UserCreation,
         CsvUpload,
     },
     data() {
         return {
             library: {},
             error: null,
             success: null,
             users: [],
             user_list_key: 0,
         }
     },
     methods: {
         refresh_users() {
             console.log("Refreshing");
             this.user_list_key = this.user_list_key + '-x';
         },
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
         this.user_list_key = 'lib' + this.$route.params.id;
     }
 }
</script>
<template>
  <div class="m-8">
    <div v-if="error" class="py-2 text-claret-900 font-bold">
      {{ $gettext(error) }}
    </div>
    <div v-if="success" class="py-2 text-spectra-800 font-bold">
      {{ $gettext(success) }}
    </div>
    <div class="grid grid-cols-1 md:grid-cols-[250px_auto] gap-4">
      <div>
        <h1 class="font-bold text-xl">{{ library.name }}</h1>
        <form @submit.prevent="update">
          <div>
            <label for="library-url">{{ $gettext('Internet address') }}</label>
            <div class="flex">
              <input class="mcrz-input" id="library-url" v-model="library.url" />
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
      <div>
        <h1 class="font-bold text-xl mb-6">{{ $gettext('Users') }}</h1>
        <DashboardTable :listing_url="'/collector/api/library/list-users/' + $route.params.id"
                        :removal_url="'/collector/api/library/remove-user/' + $route.params.id"
                        :key="user_list_key" />
        <h1 class="font-bold text-xl my-6">{{ $gettext('Add User') }}</h1>
        <UserCreation :library_id="$route.params.id" @user-created="refresh_users"/>
      </div>
    </div>
    <div>
      <CsvUpload :library_id="library_id" />
    </div>
  </div>
</template>
