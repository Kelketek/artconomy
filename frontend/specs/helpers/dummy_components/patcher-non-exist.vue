<template>
  <div>
    <div id="max_load">{{maxLoad.model}}</div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Patch} from '@/store/singles/patcher'
import {ProfileController} from '@/store/profiles/controller'

  @Component
export default class PatcherNonExist extends Vue {
    public subjectHandler: ProfileController = null as unknown as ProfileController
    public maxLoad: Patch = null as unknown as Patch

    public created() {
      this.maxLoad = this.$makePatcher({modelProp: 'subjectHandler.user', debounceRate: 200, attrName: 'max_load'})
      this.subjectHandler = this.$getProfile('Fox', {})
    }
}
</script>

<style scoped>

</style>
