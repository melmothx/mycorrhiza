<script>
 import axios from 'axios'
 export default {
     emits: [
         'refetch',
     ],
     props: [
         'record',
     ],
     methods: {
         remove() {
             const vm = this;
             console.log("Removing...");
             if (vm.record.id) {
                 console.log("Removing " + vm.record.id)
                 axios.post('/collector/api/exclusions',
                            {
                                id: vm.record.id,
                                op: 'delete',
                            },
                            {
                                "xsrfCookieName": "csrftoken",
                                "xsrfHeaderName": "X-CSRFToken",
                            })
                      .then(function(res) {
                          console.log(res.data);
                          vm.$emit('refetch');
                      });
             }
         }
     }
 }
</script>
<template>
  <td>
    <button class="rounded bg-pink-500 hover:bg-pink-700 text-white font-semibold px-2 m-3"
            @click="remove">Restore</button>
  </td>
  <td class="p-1 border">
    {{ record.target }}
  </td>
  <td class="p-1 border">
    {{ record.type }}
  </td>
  <td class="p-1 border">
    {{ record.comment }}
  </td>
  <td class="p-1 border">
    {{ record.created }}
  </td>
</template>
