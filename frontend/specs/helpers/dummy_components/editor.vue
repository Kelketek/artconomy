<template>
  <div>
    <ac-editor v-model="stuff" id="editor" ref="auto"></ac-editor>
    <ac-editor v-model="things" id="editor-manual" :auto-save="false" :save-comparison="base" ref="manual"></ac-editor>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import AcEditor from '@/components/fields/AcEditor.vue'

  @Component({
    components: {AcEditor},
  })
export default class Editor extends Vue {
    public stuff = ''
    public things = ''
    public base = ''
}
</script>
