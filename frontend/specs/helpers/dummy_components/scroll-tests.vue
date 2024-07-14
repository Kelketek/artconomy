<template>
  <div>
    <div v-if="test === 'scrollableText'">
      <div id="form-example">
        <div class="scrollableText">
          <span class="error--text" id="scrollable-text-error"></span>
        </div>
      </div>
    </div>
    <div v-else-if="test === 'idOnly'">
      <div id="form-example">
        <span class="error--text" id="id-only-error"></span>
      </div>
    </div>
    <div v-else-if="test === 'noError'">
      <div id="form-example"></div>
    </div>
    <div v-else-if="test === 'noErrorNoId'">

    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{test?: string}>()
</script>
