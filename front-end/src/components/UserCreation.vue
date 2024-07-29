<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     props: [ 'library_id' ],
     emits: [ 'UserCreated' ],
     data() {
         return {
             error: null,
             success: null,
             email: null,
             username: null,
             first_name: null,
             last_name: null,
             user_exists: false,
         }
     },
     methods: {
         reset_all() {
             this.error = null;
             this.success = null;
             this.email = null;
             this.username = null;
             this.first_name = null;
             this.last_name = null;
             this.user_exists = false;
         },
         create_user() {
             if (this.username) {
                 let user = {
                     username: this.username,
                     email: this.email,
                     first_name: this.first_name || '',
                     last_name: this.last_name || '',
                 };
                 axios.post('/collector/api/library/create-user/' + this.library_id, user)
                      .then(res => {
                          this.reset_all();
                          this.error = res.data.error;
                          this.success = res.data.success;
                          this.$emit('UserCreated');
                      })
                      .catch(error => {
                          this.error = error;
                          this.success = null;
                      });
             }
         },
         check_username() {
             if (this.username) {
                 axios.get('/collector/api/auth/user-check/' + this.username)
                      .then(res => {
                          if (res.data.username_exists) {
                              this.user_exists = true;
                          }
                          else {
                              this.user_exists = false;
                          }
                      })
                      .catch(error => {
                          this.error = error;
                      });
             }
         },
     },
     mounted() {
         this.reset_all();
     },
     watch: {
         username(old_username, new_username) {
             this.check_username(new_username)
         }
     }
 }
</script>
<template>
  <div v-if="error" class="py-2 text-claret-900 font-bold">
    {{ $gettext(error) }}
  </div>
  <div v-if="success" class="py-2 text-spectra-800 font-bold">
    {{ $gettext(success) }}
  </div>
  <form @submit.prevent="create_user">
    <div>
      <label for="user-username">
        {{ $gettext('Username') }}
        <span class="text-claret-900 font-bold" v-if="user_exists">{{ $gettext('This username already exist. You are going to add it to this library.') }}</span>
      </label>
      <div class="flex">
        <input class="mcrz-input" id="user-username" v-model="username" required/>
      </div>
    </div>
    <div>
      <label for="user-email">{{ $gettext('Email') }}</label>
      <div class="flex">
        <input type="email" class="mcrz-input" id="user-email" v-model="email" />
      </div>
    </div>
    <div>
      <label for="user-first-name">{{ $gettext('First Name') }}</label>
      <div class="flex">
        <input class="mcrz-input" id="user-first-name" v-model="first_name" />
      </div>
    </div>
    <div>
      <label for="user-last-name">{{ $gettext('Last Name') }}</label>
      <div class="flex">
        <input class="mcrz-input" id="user-last-name" v-model="last_name" />
      </div>
    </div>
    <div class="mt-2">
      <button class="btn-primary p-1" type="submit">{{ $gettext('Add') }}</button>
    </div>
  </form>
</template>
