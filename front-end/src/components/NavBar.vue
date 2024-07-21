<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import {
     Listbox,
     ListboxButton,
     ListboxOptions,
     ListboxOption,
     Menu, MenuButton, MenuItems, MenuItem,
 } from '@headlessui/vue'
 import { ChevronUpDownIcon, UserIcon } from '@heroicons/vue/24/solid'

 export default {
     emits: [
         'refetchResults',
     ],
     components: {
         Listbox,
         ListboxButton,
         ListboxOptions,
         ListboxOption,
         Menu, MenuButton, MenuItems, MenuItem,
         ChevronUpDownIcon, UserIcon,
     },
     data() {
         return {
             username: null,
             password: null,
             authenticated: null,
             user_data: {},
             message: null,
             reset_message: null,
             current_language: null,
         }
     },
     methods: {
         check() {
             const vm = this;
             console.log("Checking user");
             axios.get('/collector/api/auth/user')
                  .then(function(res) {
                      console.log(res.data);
                      vm.authenticated = res.data.logged_in;
                      vm.user_data = res.data
                      vm.message = null;
                      vm.reset_message = null;
                  });
         },
         login() {
             const vm = this;
             vm.message = "";
             vm.reset_message = null;
             axios.post('/collector/api/auth/login', {
                 "username": this.username,
                 "password": this.password,
             }).then(function(res) {
                 if (res.data.logged_in) {
                     vm.authenticated = res.data.logged_in;
                     vm.user_data = res.data
                     vm.message = null;
                     vm.$emit('refetchResults');
                 }
                 else {
                     vm.message = res.data.error || "Failed login";
                 }
             });
         },
         password_reset() {
             const vm = this;
             vm.message = "";
             axios.post('/collector/api/auth/reset-password', {
                 "operation": "send-link",
                 "username":  this.username,
             }).then(function(res) {
                 console.log(res.data.message);
                 vm.message = "";
                 vm.reset_message = res.data.message;
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
         set_language() {
             if (this.current_language != this.$getlanguage()) {
                 this.$setlanguage(this.current_language);
                 location.reload();
             }
         }
     },
     mounted() {
         this.check();
         this.current_language = this.$getlanguage();
     },
 }
</script>
<template>
  <div class="flex m-3">
    <div class="flex-grow">
      <a href="/">
        <img class="h-16" src="/logobanner.png" :alt="$gettext('Home')" />
      </a>
    </div>
    <div v-if="authenticated">
      <span class="px-3">{{ $gettext('Hello, %1!', authenticated) }}</span>
    </div>
    <div v-else>
      <form @submit.prevent="login" class="ml-4">
        <input class="outline outline-0 border border-gray-300 focus:border-spectra-500 focus:ring-0 px-2 rounded-none h-8 w-32"
               :placeholder="$gettext('Username')"
               type="text" v-model="username" required>
        <input class="outline outline-0 border border-gray-300 focus:border-spectra-500 focus:ring-0 px-2 h-8 w-32"
               :placeholder="$gettext('Password')"
               type="password" v-model="password" required>
        <button class="h-8 btn-secondary rounded-none rounded-br-3xl pr-10 pl-4 italic font-normal h-8 mr-2"
                type="submit">{{ $gettext('Login') }}</button>
      </form>
      <div v-if="message" class="pt-2">
        <form @submit.prevent="password_reset" class="ml-4">
          <div class="py-2 text-claret-900 font-bold">
            {{ $gettext(message) }}
          </div>
          <button id="reset-password"
                  class="h-8 btn-secondary rounded-none rounded-br-3xl pr-10 pl-4 italic font-normal h-8 mr-2"
                  type="submit">{{ $gettext('Reset Password for %1?', username) }}</button>
        </form>
      </div>
      <div v-if="reset_message" class="p-2 ml-4 text-claret-900 font-bold" @click="reset_message = null">
        {{ $gettext(reset_message) }}
      </div>
    </div>

    <div v-if="authenticated">
      <Menu as="div" class="relative z-10">
        <div>
          <MenuButton class="inline-flex w-full justify-center text-spectra-800 h-8 p-1">
            <UserIcon class="h-5 w-5" title="User Menu" />
            <ChevronUpDownIcon class="h-5 w-5" aria-hidden="true"/>
          </MenuButton>
        </div>
        <transition
            enter-active-class="transition duration-100 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-75 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0">
          <MenuItems class="absolute right-0 mt-1 max-h-60 overflow-auto bg-perl-bush-50 p-0 shadow-lg rounded-br-3xl">
            <MenuItem v-if="user_data.is_superuser" class="cursor-pointer hover:text-spectra-800 py-1 px-2">
              <a href="/admin">
                {{ $gettext('Admin') }}
              </a>
            </MenuItem>
            <MenuItem v-if="user_data.is_superuser || user_data.is_library_admin" class="cursor-pointer hover:text-spectra-800 py-1 px-2">
              <div @click="$router.push({ name: 'dashboard', params: { type: 'exclusions' } })">
                {{ $gettext('Exclusions') }}
              </div>
            </MenuItem>
            <template v-if="user_data.is_library_admin">
              <template v-for="lib in user_data.libraries">
                <MenuItem class="cursor-pointer hover:text-spectra-800 py-1 px-2">
                  <div @click="$router.push({ name: 'library_edit', params: { id: lib.id }})">
                    {{ lib.name }}
                  </div>
                </MenuItem>
              </template>
            </template>
            <MenuItem class="cursor-pointer hover:text-spectra-800 py-1 px-2">
              <div @click="logout">
                {{ $gettext('Logout') }}
              </div>
            </MenuItem>
          </MenuItems>
        </transition>
      </Menu>
    </div>
    <div :title="$gettext('UI language')">
      <Listbox v-model="current_language">
        <div class="relative m-0">
          <ListboxButton class="relative w-full cursor-pointer py-1 h-8 pl-3 pr-10 text-left shadow-md text-sm bg-perl-bush-50 rounded"
                         v-slot="{ open }">
            <span class="block truncate font-bold">{{ current_language }}</span>
            <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronUpDownIcon
                  class="h-5 w-5 text-gray-400"
                  aria-hidden="true"
              />
            </span>
          </ListboxButton>
          <transition
              enter-active-class="transition duration-100 ease-out"
              enter-from-class="transform scale-95 opacity-0"
              enter-to-class="transform scale-100 opacity-100"
              leave-active-class="transition duration-75 ease-in"
              leave-from-class="transform scale-100 opacity-100"
              leave-to-class="transform scale-95 opacity-0">
            <ListboxOptions class="absolute mt-1 max-h-60 w-full overflow-auto bg-perl-bush-50 pl-3 text-base shadow-lg rounded">
              <ListboxOption v-for="lang in ['en', 'it']"
                             :value="lang" :key="lang"
                             @click="set_language"
                             class="cursor-pointer hover:text-spectra-800"
              >{{ lang }}</ListboxOption>
            </ListboxOptions>
          </transition>
        </div>
      </Listbox>
    </div>
  </div>
</template>
