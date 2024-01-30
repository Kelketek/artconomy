<template>
  <div>
    <div id="sfw_mode">{{subjectHandler.user.patchers.sfw_mode.model}}</div>
    <div id="max_load">{{subjectHandler.artistProfile.patchers.max_load.model}}</div>
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
    public localShare: SingleController<DeliverableViewSettings> = null as unknown as SingleController<DeliverableViewSettings>

    public created() {
      this.subjectHandler = this.$getProfile('Fox', {})
      this.subjectHandler.artistProfile.setX(genArtistProfile())
      this.localShare = this.$getSingle('TestSingle', {endpoint: '#'})
    }
}

export default toNative(Patcher)
</script>

<style scoped>

</style>
