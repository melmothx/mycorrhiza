<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import SiteLogo from './SiteLogo.vue';
 import { bookbuilder } from '../stores/bookbuilder.js'
 import {
     Listbox,
     ListboxButton,
     ListboxOptions,
     ListboxOption,
     Menu, MenuButton, MenuItems, MenuItem,
 } from '@headlessui/vue'
 import {
     ChevronUpDownIcon,
     UserIcon,
     BookOpenIcon,
 } from '@heroicons/vue/24/solid'

 export default {
     emits: [
         'refetchResults',
     ],
     components: {
         SiteLogo,
         Listbox,
         ListboxButton,
         ListboxOptions,
         ListboxOption,
         Menu, MenuButton, MenuItems, MenuItem,
         ChevronUpDownIcon, UserIcon,
         BookOpenIcon,
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
             show_login: false,
             bookbuilder,
         }
     },
     methods: {
         check() {
             console.log("Checking user");
             axios.get('/collector/api/auth/user')
                  .then((res) => {
                      console.log(res.data);
                      this.authenticated = res.data.logged_in;
                      this.user_data = res.data
                      this.message = res.data.message;
                      this.reset_message = null;
                  });
         },
         login() {
             this.message = "";
             this.reset_message = null;
             axios.post('/collector/api/auth/login', {
                 "username": this.username,
                 "password": this.password,
             }).then((res) => {
                 if (res.data.logged_in) {
                     this.authenticated = res.data.logged_in;
                     this.user_data = res.data
                     this.message = null;
                     this.$emit('refetchResults');
                 }
                 else {
                     this.message = res.data.error || "Failed login";
                 }
             });
         },
         password_reset() {
             this.message = "";
             axios.post('/collector/api/auth/reset-password', {
                 "operation": "send-link",
                 "username":  this.username,
             }).then((res) => {
                 console.log(res.data.message);
                 this.message = "";
                 this.reset_message = res.data.message;
             });
         },
         logout() {
             axios.get('/collector/api/auth/logout')
                  .then((res) => {
                      this.show_login = false;
                      this.$emit('refetchResults');
                      this.check();
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
         this.bookbuilder.restore();
     },
 }
</script>
<template>
  <header>
  <div class="flex flex-wrap m-3 items-center">
    <div class="grow">
      <SiteLogo />
    </div>
    <div :title="$gettext('UI language')">
      <Listbox v-model="current_language">
        <div class="relative m-0">
          <ListboxButton class="relative w-full cursor-pointer py-1 h-8 pl-3 pr-10 text-left shadow-md text-sm bg-perl-bush-50 rounded-sm"
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
            <ListboxOptions class="absolute mt-1 max-h-60 w-full overflow-auto bg-perl-bush-50 pl-3 text-base shadow-lg rounded-sm">
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
    <div v-if="authenticated">
      <span class="px-3">{{ $gettext('Hello, %1!', authenticated) }}</span>
    </div>
    <div v-else>
      <UserIcon class="h-5 w-5 mx-2 text-spectra-800 cursor-pointer" @click="show_login = show_login ? false : true" />
    </div>
    <div v-if="bookbuilder.session_id">
      <router-link :to="{ name: 'bookbuilder' }">
        <BookOpenIcon class="h-5 w-5 text-cab-sav-800 cursor-pointer" />
      </router-link>
    </div>
    <div v-if="authenticated">
      <Menu as="div" class="relative z-10">
        <div>
          <MenuButton class="inline-flex w-full justify-center text-spectra-800 h-8 p-1">
            <UserIcon class="h-5 w-5" :title="$gettext('User Menu')" />
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
            <MenuItem class="cursor-pointer hover:text-spectra-800 py-1 px-2">
              <div>
                <router-link :to="{ name: 'dashboard', params: { type: 'exclusions' } }">
                  {{ $gettext('Exclusions') }}
                </router-link>
              </div>
            </MenuItem>
            <template v-if="user_data.is_library_admin">
              <template v-for="lib in user_data.libraries">
                <MenuItem class="cursor-pointer hover:text-spectra-800 py-1 px-2">
                  <div>
                    <router-link :to="{ name: 'library_edit', params: { id: lib.id }}">
                      {{ lib.name }}
                    </router-link>
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
  </div>
  <div v-if="!authenticated && show_login">
    <form @submit.prevent="login" class="mx-4 flex">
      <input class="outline outline-0 border border-gray-300 focus:border-spectra-500 focus:ring-0 px-2 rounded-none h-8 w-full"
             :placeholder="$gettext('Username')"
             type="text" v-model="username" required>
      <input class="outline outline-0 border border-gray-300 focus:border-spectra-500 focus:ring-0 px-2 h-8 w-full"
             :placeholder="$gettext('Password')"
             type="password" v-model="password" required>
      <button class="h-8 btn-secondary rounded-none rounded-br-3xl pr-10 pl-4 italic font-normal h-8 mr-2"
              type="submit">{{ $gettext('Login') }}</button>
    </form>
    <div v-if="message" class="pt-2">
      <div class="ml-4 py-2 text-claret-900 font-bold">
        {{ $gettext(message) }}
      </div>
      <form v-if="username" @submit.prevent="password_reset" class="ml-4">
        <button id="reset-password"
                class="h-8 btn-secondary rounded-none rounded-br-3xl pr-10 pl-4 italic font-normal h-8 mr-2"
                type="submit">{{ $gettext('Reset Password for %1?', username) }}</button>
      </form>
    </div>
    <div v-if="reset_message" class="p-2 ml-4 text-claret-900 font-bold" @click="reset_message = null">
      {{ $gettext(reset_message) }}
    </div>
  </div>
  </header>
</template>
