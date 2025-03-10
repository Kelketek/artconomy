<template>
  <div>
    <div
      v-if="editing"
      class="is-editing"
      @click="editing=false"
    >
      Editing
    </div>
    <div
      v-else
      class="is-not-editing"
      @click="editing=true"
    >
      Not Editing
    </div>
  </div>
</template>

<script setup lang="ts">
import {useEditable} from '@/mixins/editable.ts'
import {computed} from 'vue'

const props = defineProps<{controls: boolean}>()
const controls = computed(() => props.controls)

const {editing} = useEditable(controls)
</script>
