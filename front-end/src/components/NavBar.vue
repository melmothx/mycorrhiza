<script>
 import axios from 'axios'
 export default {
     emits: [
         'refetchResults',
     ],
     data() {
         return {
             username: null,
             password: null,
             authenticated: null,
             message: null,
             current_language: null,
         }
     },
     methods: {
         check() {
             const vm = this;
             console.log("Checking user");
             axios.get('/collector/api/auth/user')
                  .then(function(res) {
                      console.log(res);
                      vm.authenticated = res.data.logged_in;
                      vm.message = null;
                  });
         },
         login() {
             const vm = this;
             vm.message = "";
             axios.post('/collector/api/auth/login', {
                 "username": this.username,
                 "password": this.password,
             }, {
                 "xsrfCookieName": "csrftoken",
                 "xsrfHeaderName": "X-CSRFToken",
             }).then(function(res) {
                 if (res.data.logged_in) {
                     vm.authenticated = res.data.logged_in;
                     vm.message = null;
                     vm.$emit('refetchResults');
                 }
                 else {
                     vm.message = res.data.error || "Failed login";
                 }
             });
         },
         logout() {
             const vm = this;
             axios.get('/collector/api/auth/logout')
                  .then(function(res) {
                      vm.$emit('refetchResults');
                      vm.check();
                  });
         },
         set_language(lang) {
             this.current_language = this.$setlanguage(lang);
             console.log(`Current language is ${this.current_language}`);
             location.reload();
         }
     },
     mounted() {
         this.check();
         this.current_language = this.$getlanguage();
     },
 }
</script>
<template>
  <div class="flex items-center m-3">
    <div class="flex-grow">
      <span @click="$router.push({ name: 'home' })">Home</span>
    </div>
    <div>
      <div v-for="lang in ['it', 'en', 'hr']">
        <span @click="set_language(lang)">
          <span v-if="lang == current_language">
            <strong>{{ lang }}</strong>
          </span>
          <span v-else>{{ lang }}</span>
        </span>
      </div>
    </div>
    <div v-if="authenticated">
      <div class="m-2" @click="$router.push({ name: 'dashboard', params: { type: 'exclusions' } })">
        {{ $gettext('Exclusions') }}
      </div>
    </div>
    <div v-if="authenticated">
      <button class="h-8 btn-secondary rounded-none rounded-bl-3xl pr-3 pl-10 ml-4 italic font-normal"
          type="button" @click="logout">{{ $gettext('Logout') }}</button>
      <span class="px-3">{{ $gettext('Hello, %1!', authenticated) }}</span>
    </div>
    <div v-else>
      <form @submit.prevent="login">
        <button class="h-8 btn-secondary rounded-none rounded-bl-3xl pr-4 pl-10 ml-4 italic font-normal"
                type="submit">{{ $gettext('Login') }}</button>
        <input class="outline outline-0 border border-gray-300 focus:border-spectra-500 focus:ring-0 px-2 rounded-none h-8"
               type="text" v-model="username" required>
        <input class="outline outline-0 border border-gray-300 focus:border-spectra-500 focus:ring-0 px-2 h-8"
               type="password" v-model="password" required>
      </form>
      <div class="px-2 text-claret-900 font-bold text-center" v-if="message">
        {{ $gettext(message) }}
      </div>
    </div>
  </div>
</template>
