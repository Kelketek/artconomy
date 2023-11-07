<template>
  <div>
    <div id="sfw_mode">{{sfwMode.model}}</div>
  </div>
</template>

<script lang="ts">
import {Component, toNative} from 'vue-facing-decorator'
import {Patch} from '@/store/singles/patcher'
import {ArtVue} from '@/lib/lib'

@Component
class PatcherBroken extends ArtVue {
    public sfwMode: Patch = null as unknown as Patch
    public created() {
      this.sfwMode = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'sfw_mode'})
    }
}
export default toNative(PatcherBroken)
</script>

<style scoped>

</style>
