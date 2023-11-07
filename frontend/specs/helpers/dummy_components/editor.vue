<template>
  <div>
    <ac-editor v-model="stuff" id="editor" ref="auto"></ac-editor>
    <ac-editor v-model="things" id="editor-manual" :auto-save="false" :save-comparison="base" ref="manual"></ac-editor>
  </div>
</template>

<script lang="ts">
import {Component, toNative} from 'vue-facing-decorator'
import AcEditor from '@/components/fields/AcEditor.vue'
import {ArtVue} from '@/lib/lib'

@Component({
  components: {AcEditor},
})
class Editor extends ArtVue {
  public stuff = ''
  public things = ''
  public base = ''
}
export default toNative(Editor)
</script>
