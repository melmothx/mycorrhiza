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
         }
     },
     methods: {
         check() {
             const vm = this;
             console.log("Checking user");
             axios.get('/search/api/auth/user')
                  .then(function(res) {
                      console.log(res);
                      vm.authenticated = res.data.logged_in;
                      vm.message = null;
                  });
         },
         login() {
             const vm = this;
             vm.message = "";
             axios.post('/search/api/auth/login', {
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
             axios.get('/search/api/auth/logout')
                  .then(function(res) {
                      vm.$emit('refetchResults');
                      vm.check();
                  });
         },
     },
     mounted() {
         this.check();
     },
 }
</script>
<template>
  <div class="flex items-center m-3">
    <div class="flex-grow"></div>
    <div v-if="authenticated">
      <span class="px-3">Hello, {{ authenticated }}!</span>
      <button class="rounded bg-pink-500 hover:bg-pink-700 text-white font-semibold px-2"
          type="button" @click="logout">Logout</button>
    </div>
    <div v-else>
      <form @submit.prevent="login">
        <input class="outline outline-0 border border-gray-300 focus:border-pink-500 focus:ring-0 px-2 rounded-l h-6"
               type="text" v-model="username" required>
        <input class="outline outline-0 border border-gray-300 focus:border-pink-500 focus:ring-0 px-2 h-6"
               type="password" v-model="password" required>
        <button class="rounded-r bg-pink-500 hover:bg-pink-700 text-white font-semibold h-6 px-2"
                type="submit">Login</button>
      </form>
    </div>
    <div class="px-2 text-red-700 font-bold" v-if="message">
      {{ message }}
    </div>
  </div>
</template>
