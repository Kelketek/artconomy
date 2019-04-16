<template>
  <div>
    <div id="sfw_mode">{{sfwMode.model}}</div>
    <div id="max_load">{{maxLoad.model}}</div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Patch} from '@/store/singles/patcher'
import {ProfileController} from '@/store/profiles/controller'
import {genArtistProfile} from '@/specs/helpers/fixtures'

  @Component
export default class Patcher extends Vue {
    public subjectHandler: ProfileController = null as unknown as ProfileController
    private maxLoad: Patch = null as unknown as Patch
    private sfwMode: Patch = null as unknown as Patch

    public created() {
      this.subjectHandler = this.$getProfile('Fox', {})
      this.subjectHandler.artistProfile.setX(genArtistProfile())
      this.maxLoad = this.$makePatcher(
        {modelProp: 'subjectHandler.artistProfile', debounceRate: 200, attrName: 'max_load'}
      )
      this.sfwMode = this.$makePatcher(
        {modelProp: 'subjectHandler.user', attrName: 'sfw_mode'}
      )
    }
}
</script>

<style scoped>

</style>
