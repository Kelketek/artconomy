<template>
  <div v-if="sfwMode !== null">
    <div id="sfw_mode">{{sfwMode.model}}</div>
    <div id="max_load">{{maxLoad.model}}</div>
  </div>
</template>

<script lang="ts">
import {Component, toNative} from 'vue-facing-decorator'
import {Patch} from '@/store/singles/patcher'
import {ProfileController} from '@/store/profiles/controller'
import {genArtistProfile} from '@/specs/helpers/fixtures'
import {SingleController} from '@/store/singles/controller'
import DeliverableViewSettings from '@/types/DeliverableViewSettings'
import {ArtVue} from '@/lib/lib'

@Component({})
class Patcher extends ArtVue {
    public subjectHandler: ProfileController = null as unknown as ProfileController
    public maxLoad: Patch = null as unknown as Patch
    public sfwMode: Patch = null as unknown as Patch
    public localShare: SingleController<DeliverableViewSettings> = null as unknown as SingleController<DeliverableViewSettings>

    public created() {
      this.subjectHandler = this.$getProfile('Fox', {})
      this.subjectHandler.artistProfile.setX(genArtistProfile())
      this.maxLoad = this.$makePatcher(
        {modelProp: 'subjectHandler.artistProfile', debounceRate: 200, attrName: 'max_load'},
      )
      this.sfwMode = this.$makePatcher(
        {modelProp: 'subjectHandler.user', attrName: 'sfw_mode'},
      )
      this.localShare = this.$getSingle('TestSingle', {endpoint: '#'})
    }
}

export default toNative(Patcher)
</script>

<style scoped>

</style>
