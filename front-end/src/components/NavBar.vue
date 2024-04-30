<script>
 import axios from 'axios'
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
      <span class="cursor-pointer" @click="$router.push({ name: 'home' })">Home</span>
    </div>
    <div>
      <Listbox v-model="current_language">
        <div class="relative m-0">
          <ListboxButton class="relative w-full cursor-pointer rounded-tl-3xl py-1 h-8 pl-3 pr-10 text-left shadow-md text-sm bg-perl-bush-50"
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
            <ListboxOptions class="absolute mt-1 max-h-60 w-full overflow-auto bg-perl-bush-50 pl-3 text-base shadow-lg">
              <ListboxOption v-for="lang in ['en', 'it']"
                             :value="lang" :key="lang"
                             @click="set_language"
                             class="cursor-pointer hover:text-spectra-800 hover:font-bold"
              >{{ lang }}</ListboxOption>
            </ListboxOptions>
          </transition>
        </div>
      </Listbox>
    </div>
    <div v-if="authenticated">
      <span class="px-3">{{ $gettext('Hello, %1!', authenticated) }}</span>
    </div>
    <div v-else>
      <form @submit.prevent="login" class="ml-4">
        <input class="outline outline-0 border border-gray-300 focus:border-spectra-500 focus:ring-0 px-2 rounded-none h-8 w-32"
               type="text" v-model="username" required>
        <input class="outline outline-0 border border-gray-300 focus:border-spectra-500 focus:ring-0 px-2 h-8 w-32"
               type="password" v-model="password" required>
        <button class="h-8 btn-secondary rounded-none rounded-br-3xl pr-10 pl-4 italic font-normal h-8 mr-2"
                type="submit">{{ $gettext('Login') }}</button>
      </form>
      <div class="px-2 text-claret-900 font-bold text-center" v-if="message">
        {{ $gettext(message) }}
      </div>
    </div>
    <div v-if="authenticated">
      <Menu as="div" class="relative">
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
            <MenuItem class="cursor-pointer hover:text-spectra-800 py-1 px-2">
              <a href="/admin">
                {{ $gettext('Admin') }}
              </a>
            </MenuItem>
            <MenuItem class="cursor-pointer hover:text-spectra-800 py-1 px-2">
              <div @click="$router.push({ name: 'dashboard', params: { type: 'exclusions' } })">
                {{ $gettext('Exclusions') }}
              </div>
            </MenuItem>
            <MenuItem class="cursor-pointer hover:text-spectra-800 py-1 px-2">
              <div @click="logout">
                {{ $gettext('Logout') }}
              </div>
            </MenuItem>
          </MenuItems>
        </transition>
      </Menu>
    </div>
  </div>
</template>
