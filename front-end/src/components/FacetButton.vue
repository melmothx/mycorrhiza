<script>
  export default {
      props: ['id', 'term', 'count', 'active', 'name', 'merge_type', 'translate_value'],
      emits: ['toggleFilter'],
      methods: {
          drag_element(e, id, label) {
              e.dataTransfer.dropEffect = 'copy';
              e.dataTransfer.effectAllowed = 'copy';
              e.dataTransfer.setData('ID', id);
              e.dataTransfer.setData('Label', label);
              e.dataTransfer.setData('Merge', this.merge_type);
          },
      },
  }
</script>
<template>
  <div class="font-serif">
    <label>
      <input type="checkbox" class="rounded focus:border-pink-500 text-pink-500 focus:ring-0"
             :checked="active"
             @change="$emit('toggleFilter', id , $event.target.checked)" />
      <span class="ml-1">
        <template v-if="merge_type">
          <span class="cursor-grab active:cursor-grabbing"
                draggable="true"
                @dragstart="drag_element($event, id, term)">
            <template v-if="translate_value">
              {{ $gettext(term) }}
            </template>
            <template v-else>
              {{ term }}
            </template>
          </span>
        </template>
        <template v-else>
          <span v-if="translate_value">
            {{ $gettext(term) }}
          </span>
          <span v-else>
            {{ term }}
          </span>
        </template>
      </span>
      ({{ count }})
    </label>
  </div>
</template>
<style scoped>
</style>
