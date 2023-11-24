<script>
 import axios from 'axios'
 export default {
     props: ['merge_type'],
     emits: ['refetchResults'],
     data() {
         return {
             merge_list: [],
             flash_success: "",
             flash_error: "",
         }
     },
     methods: {
         onDrop(e) {
             const id = e.dataTransfer.getData('ID');
             const label = e.dataTransfer.getData('Label');
             const merge_type = e.dataTransfer.getData('Merge');
             this.clear_flash_error();
             this.clear_flash_success();
             if (id && label && merge_type && merge_type == this.merge_type) {
                 console.log("Dropping entry: " + id + " " + label);
                 this.merge_list.push({
                     "id": id,
                     "label": label,
                 });
             }
         },
         clear_list() {
             this.merge_list = [];
         },
         clear_flash_error() {
             this.flash_error = '';
         },
         clear_flash_success() {
             this.flash_success = '';
         },
         merge_records() {
             const vm = this;
             axios.post('/search/api/merge/' + vm.merge_type, vm.merge_list)
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
  <div @drop="onDrop($event)" @dragover.prevent @dragenter.prevent>
    <div class="bg-gray-200 font-semibold 
                rounded-t border-t border-s border-e border-gray-300 p-2 -space-y-px">
      <h5>Drop {{ merge_type }} here for merging</h5>
    </div>
    <div class="rounded-b border border-gray-300">
      <ul role="list">
        <li class="border-b p-2 font-serif text-sm"
            v-for="entry in merge_list">
          {{ entry.label }}
        </li>
      </ul>
      <div class="flex justify-center items-center m-2">
        <div class="px-2">
          <button class="bg-pink-500 hover:bg-pink-700 text-white font-semibold rounded px-2 py-1 text-sm"
                  type="button" @click="merge_records">Merge</button>
        </div>
        <div class="px-2">
          <button class="bg-pink-500 hover:bg-pink-700 text-white font-semibold rounded px-2 py-1 text-sm"
                  type="button" @click="clear_list">Clear</button>
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
