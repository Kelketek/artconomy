<template>
  <div>
    <ac-editor id="editor" ref="auto" v-model="stuff" />
    <ac-editor
      id="editor-manual"
      ref="manual"
      v-model="things"
      :auto-save="false"
      :save-comparison="base"
    />
  </div>
</template>

<script setup lang="ts">
import AcEditor from "@/components/fields/AcEditor.vue"
import { ref } from "vue"

const stuff = ref("")
const things = ref("")
const base = ref("")
</script>
