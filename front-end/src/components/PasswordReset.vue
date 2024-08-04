<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 export default {
     props: [
         'username',
         'token',
     ],
     data() {
         return {
             error: null,
             password: null,
             password_repeat: null,
         }
     },
     methods: {
         reset_password() {
             this.error = null;
             axios.post('/collector/api/auth/reset-password', {
                 "operation": "reset",
                 "username": this.username,
                 "token": this.token,
                 "password": this.password,
             }).then((res) => {
                 if (res.data.logged_in) {
                     this.$router.push({ name: 'home' });
                 }
                 else {
                     this.error = res.data.error;
                 }
             });
         }
     },
     computed: {
         ready_to_go() {
             if (this.password
                 && this.password_repeat
                 && this.password_repeat === this.password) {
                 return true;
             }
             else {
                 return false;
             }
         },
         has_mismatch() {
             if (this.password
                 && this.password_repeat
                 && this.password_repeat !== this.password) {
                 return true;
             }
         }
     }
     
 }
</script>
<template>
  <h1 class="text-xl text-center font-semibold mt-8 mb-4">
    {{ $gettext('Reset password for %1', username) }}
  </h1>
  <form @submit.prevent="reset_password">
  <div class="text-center p-2">
    <input class="mcrz-input shadow w-64"
           @input="error = ''"
           type="password" :placeholder="$gettext('Password')" v-model="password"/>
  </div>
  <div class="text-center p-2">
    <input class="mcrz-input shadow w-64"
           type="password" :placeholder="$gettext('Repeat Password')" v-model="password_repeat"/>
    <p v-if="has_mismatch" class="text-claret-900 font-bold">
      {{ $gettext('The passwords do not match') }}
    </p>
  </div>
  <div v-if="ready_to_go" class="text-center p-2">
    <button class="h-8 btn-secondary rounded-none italic font-normal w-64"
            type="submit">
      {{ $gettext('Reset password for %1', username) }}
    </button>
    <p v-if="error" class="text-claret-900 font-bold">
      {{ $gettext(error) }}
    </p>
  </div>
  <div v-else class="text-center p-2 font-bold">
    {{ $gettext('Please type your new password in both fields') }}
  </div>
  </form>
</template>
