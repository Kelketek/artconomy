<template>
  <div>
    <div id="max_load">{{maxLoad.model}}</div>
  </div>
</template>

<script lang="ts">
import {Component, toNative} from 'vue-facing-decorator'
import {Patch} from '@/store/singles/patcher'
import {ProfileController} from '@/store/profiles/controller'
import {ArtVue} from '@/lib/lib'

@Component
class PatcherNonExist extends ArtVue {
    public subjectHandler: ProfileController = null as unknown as ProfileController
    public maxLoad: Patch = null as unknown as Patch

    public created() {
      this.subjectHandler = this.$getProfile('Fox', {})
      this.maxLoad = this.$makePatcher({modelProp: 'subjectHandler.user', debounceRate: 200, attrName: 'max_load'})
    }
}
export default toNative(PatcherNonExist)
</script>

<style scoped>

</style>
