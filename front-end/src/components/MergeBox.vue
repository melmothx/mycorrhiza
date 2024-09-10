<script>
 import CreateEntityBox from './CreateEntityBox.vue'
 import HelpPopUp from './HelpPopUp.vue'
 import { TrashIcon, Cog8ToothIcon } from '@heroicons/vue/24/solid'
 import axios from 'axios'
 export default {
     components: { CreateEntityBox, TrashIcon, Cog8ToothIcon, HelpPopUp },
     props: [
         'merge_type',
         'remove_merged_filter',
         'api_call',
         'create_item',
         'dashboard',
         'help_text',
     ],
     emits: [
         'refetchResults',
         'removeMergedFilter',
     ],
     data() {
         return {
             canonical: null,
             merge_list: [],
             flash_success: "",
             flash_error: "",
             working: false,
         }
     },
     methods: {
         set_canonical_aggregation(id, label) {
             console.log("Setting canonical to " + id + ' ' + label);
             this.handle_item('set_canonical', id, label, 'entry');
         },
         set_canonical_agent(id, label) {
             console.log("Setting canonical agent to " + id + ' ' + label);
             this.handle_item('set_canonical', id, label, 'author');
         },
         drag_element(e, id, label) {
             e.dataTransfer.dropEffect = 'copy';
             e.dataTransfer.effectAllowed = 'copy';
             e.dataTransfer.setData('ID', id);
             e.dataTransfer.setData('Label', label);
             e.dataTransfer.setData('Merge', this.merge_type);
         },
         drop_element(e, op) {
             const id = e.dataTransfer.getData('ID');
             const label = e.dataTransfer.getData('Label');
             const merge_type = e.dataTransfer.getData('Merge');
             this.handle_item(op, id, label, merge_type);
         },
         handle_item(op, id, label, merge_type) {
             this.clear_flash_error();
             this.clear_flash_success();
             if (id && label && merge_type && merge_type == this.merge_type) {
                 console.log("Dropping entry: " + id + " " + label);
                 if (op && op == 'set_canonical') {
                     if (this.canonical) {
                         this.merge_list.push(this.canonical);
                     }
                     this.canonical = null;
                 }
                 if (this.canonical) {
                     this.merge_list.push({
                         "id": id,
                         "label": label,
                     });
                 }
                 else {
                     this.canonical = {
                         "id": id,
                         "label": label,
                     };
                 }
                 // check if there are duplicates or worse, recursive
                 if (this.canonical) {
                     const canonical_id = this.canonical.id;
                     const seen = {}
                     seen[canonical_id] = true;
                     let filtered = [];
                     filtered = this.merge_list.filter(function(item) {
                         if (seen[item.id]) {
                             return false;
                         }
                         else {
                             seen[item.id] = true;
                             return true;
                         }
                     });
                     console.log(filtered);
                     this.merge_list = filtered;
                 }
             }
             else {
                 this.flash_error = "I cannot do that";
             }
         },
         clear_list() {
             this.canonical = null;
             this.merge_list = [];
         },
         remove_from_list(id) {
             if (id) {
                 this.merge_list = this.merge_list.filter((i) => i.id != id);
             }
         },
         clear_flash_error() {
             this.flash_error = '';
         },
         clear_flash_success() {
             this.flash_success = '';
         },
         merge_records() {
             const vm = this;
             const params = vm.merge_list.slice();
             params.unshift(vm.canonical);
             vm.working = true;
             const api_call = vm.api_call || ('merge/' + vm.merge_type);
             axios.post('/collector/api/' + api_call, params, {
                 "xsrfCookieName": "csrftoken",
                 "xsrfHeaderName": "X-CSRFToken",
             })
                  .then(function(res) {
                      console.log(res.data)
                      if (res.data && res.data.success) {
                          if (vm.remove_merged_filter) {
                              vm.$emit('removeMergedFilter', vm.remove_merged_filter, vm.merge_list.map((el) => el.id));
                          }
                          vm.clear_list();
                          // emit a refetch
                          // vm.getResults();
                          vm.flash_success = "Done!";
                          vm.$emit('refetchResults');
                      }
                      else if (res.data)  {
                          vm.flash_error = res.data.error || "Failed!"
                      }
                      else {
                          vm.flash_error = "Failed!"
                      }
                      vm.working = false;
                  })
                  .catch(function(error) {
                      vm.working = false;
                      console.log(error)
                  });
         }
     }
 }
</script>
<template>
  <div>
    <div @drop="drop_element($event)" @dragover.prevent @dragenter.prevent
        class="bg-gradient-to-tr from-old-copper-700 to-old-copper-600 font-semibold rounded-tr-3xl p-2">
      <h2 class="text-white pl-2 text-sm">
        <span class="flex">
          <span class="grow text-white">
            <slot>Drop {{ merge_type }} here for merging</slot>
          </span>
          <span v-if="dashboard"
                class="text-white mr-2 cursor-pointer hover:text-spectra-200"
                :title="$gettext('Admin')"
                @click="$router.push({ name: 'dashboard', params: { type: dashboard } })">
            <Cog8ToothIcon class="m-1 h-4 w-4" />
          </span>
          <HelpPopUp v-if="help_text">
            {{ $gettext(help_text) || $gettext('Missing help, sorry...') }}
          </HelpPopUp>
        </span>
      </h2>
    </div>
    <div v-if="canonical"
         @drop="drop_element($event, 'set_canonical')" @dragover.prevent @dragenter.prevent
         class="border-r border-l border-t border-gray-300 bg-perl-bush-50">
      <h3 class="font-serif p-2 font-semibold text-sm flex justify-between">
        <span>
          {{ canonical.label }}
        </span>
        <span v-if="!working"
              class="cursor-pointer text-claret-800 hover:text-claret-600"
              title="$gettext('Clear list')"
              @click="clear_list">
          <TrashIcon class="h-4 w-4" />
        </span>
      </h3>
    </div>
    <div class="border border-gray-300 bg-perl-bush-50"
         @drop="drop_element($event)" @dragover.prevent @dragenter.prevent>
      <ul role="list" >
        <li v-for="entry in merge_list" :key="entry.id" class="border-b p-2 font-serif text-sm">
          <div class="flex justify-between">
            <span class="cursor-grab active:cursor-grabbing"
                  draggable="true"
                  @dragstart="drag_element($event, entry.id, entry.label)">
              {{ entry.label }}
            </span>
            <span v-if="!working"
                  class="cursor-pointer text-claret-800 hover:text-claret-600"
                  title="Remove"
                  @click="remove_from_list(entry.id)">
              <TrashIcon class="h-4 w-4"/>
            </span>
          </div>
        </li>
      </ul>
      <div>
        <div class="m-2 text-center" v-if="canonical && merge_list.length && !working">
          <button class="btn-primary pl-3 py-1 pr-4 pl-1 h-8 rounded-br-3xl"
                  type="button" @click="merge_records">{{ $gettext('Merge') }}</button>
        </div>
        <div v-else>
          <div v-if="!flash_error && !flash_success && !working" class="h-10"></div>
        </div>
        <div v-if="flash_error"
             @click="clear_flash_error"
             class="flex justify-center items-center m-2 cursor-pointer text-claret-900
                   mt-2 font-semibold">
          {{ $gettext(flash_error) }}
        </div>
        <div v-if="flash_success"
             @click="clear_flash_success"
             class="flex justify-center items-center m-2 cursor-pointer text-spectra-800
                   mt-2 font-bold">
          {{ $gettext(flash_success) }}
        </div>
        <div v-if="working" class="m-2 text-center">
          <span class="animate-ping rounded-full text-claret-900 p-2">{{ $gettext('Working') }}</span>
        </div>
      </div>
    </div>
    <div v-if="create_item && create_item == 'aggregation'">
      <CreateEntityBox @created-entity="set_canonical_aggregation" creation_type="aggregation" />
    </div>
    <div v-if="create_item && create_item == 'agent'">
      <CreateEntityBox @created-entity="set_canonical_agent" creation_type="agent" />
    </div>
  </div>
</template>
<style scoped>
</style>
