<template>
  <div>
    <div v-if="test === 'scrollableText'">
      <div id="form-example">
        <div class="scrollableText">
          <span id="scrollable-text-error" class="error--text" />
        </div>
      </div>
    </div>
    <div v-else-if="test === 'idOnly'">
      <div id="form-example">
        <span id="id-only-error" class="error--text" />
      </div>
    </div>
    <div v-else-if="test === 'noError'">
      <div id="form-example" />
    </div>
    <div v-else-if="test === 'noErrorNoId'" />
  </div>
</template>

<script setup lang="ts">
defineProps<{ test?: string }>()
</script>
