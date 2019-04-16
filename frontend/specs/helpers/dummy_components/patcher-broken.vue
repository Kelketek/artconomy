<template>
  <div>
    <div id="sfw_mode">{{sfwMode.model}}</div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Patch} from '@/store/singles/patcher'

  @Component
export default class PatcherBroken extends Vue {
    private sfwMode: Patch = null as unknown as Patch
    public created() {
      this.sfwMode = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'sfw_mode'})
    }
}
</script>

<style scoped>

</style>
