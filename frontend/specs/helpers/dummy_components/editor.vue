<template>
  <div>
    <ac-editor v-model="stuff" id="editor" ref="auto"></ac-editor>
    <ac-editor v-model="things" id="editor-manual" :auto-save="false" :save-comparison="base" ref="manual"></ac-editor>
  </div>
</template>

<script setup lang="ts">
import AcEditor from '@/components/fields/AcEditor.vue'
import {ref} from 'vue'

const stuff = ref('')
const things = ref('')
const base = ref('')
</script>
