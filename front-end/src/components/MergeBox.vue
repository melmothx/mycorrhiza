<script>
 import axios from 'axios'
 export default {
     props: ['merge_type'],
     emits: ['refetchResults'],
     data() {
         return {
             canonical: null,
             merge_list: [],
             flash_success: "",
             flash_error: "",
         }
     },
     methods: {
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
                     filtered = this.merge_list.filter(function(item, pos, self) {
                         if (seen.hasOwnProperty(item.id)) {
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
             axios.post('/search/api/merge/' + vm.merge_type, params)
                  .then(function(res) {
                      console.log(res.data)
                      if (res.data && res.data.success) {
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
                  })
                  .catch(function(error) {
                      console.log(error)
                  });
         }
     }
 }
</script>
<template>
  <div>
    <div @drop="drop_element($event)" @dragover.prevent @dragenter.prevent
        class="bg-gray-200 font-semibold
               rounded-t border-t border-s border-e border-gray-300 p-2 -space-y-px">
      <h2><slot>Drop {{ merge_type }} here for merging</slot></h2>
    </div>
    <div v-if="canonical"
         @drop="drop_element($event, 'set_canonical')" @dragover.prevent @dragenter.prevent
         class="border-r border-l border-t border-gray-300">
      <h3 class="font-serif p-2 font-semibold text-sm flex justify-between">
        <span>
          {{ canonical.label }}
        </span>
        <span class="cursor-pointer font-bold"
              title="Clear list" @click="clear_list">
          <span class="border-2 rounded-lg text-red-800 hover:text-black border-red-800 border px-1 mt-1">
            &#x2715;
          </span>
        </span>
      </h3>
    </div>
    <div class="rounded-b border border-gray-300"
         @drop="drop_element($event)" @dragover.prevent @dragenter.prevent>
      <ul role="list" >
        <li v-for="entry in merge_list" class="border-b p-2 font-serif text-sm">
          <div class="flex justify-between">
            <span class="cursor-grab active:cursor-grabbing"
                  draggable="true"
                  @dragstart="drag_element($event, entry.id, entry.label)">
              {{ entry.label }}
            </span>
            <span class="cursor-pointer font-bold"
                  title="Remove" @click="remove_from_list(entry.id)">
              <span class="border-2 rounded-lg hover:bg-red-300 text-red-800 border-red-800 px-1 mt-1">
                &#x2715;
              </span>
            </span>
          </div>
        </li>
      </ul>
      <div class="flex justify-center items-center m-2">
        <div class="px-2 h-7">
          <div v-if="canonical && merge_list.length">
            <button class="bg-pink-500 hover:bg-pink-700 text-white font-semibold rounded px-2 py-1 text-sm"
                    type="button" @click="merge_records">Merge</button>
          </div>
        </div>
      </div>
      <div v-if="flash_error"
           @click="clear_flash_error"
           class="flex justify-center items-center m-2 cursor-pointer text-pink-700
                 mt-2 font-semibold">
        {{ flash_error }}
      </div>
      <div v-if="flash_success"
           @click="clear_flash_success"
           class="flex justify-center items-center m-2 cursor-pointer text-green-800
                 mt-2 font-bold">
        {{ flash_success }}
      </div>
    </div>
  </div>
</template>
<style scoped>
</style>
