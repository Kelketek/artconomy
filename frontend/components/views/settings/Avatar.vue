<template>
  <v-layout row wrap pt-4 id="avatar-settings">
    <v-flex d-flex text-xs-center xs12 sm3 lg3 offset-sm2 offset-lg3>
      <v-card>
        <v-card-text>
          <v-subheader>Current Avatar</v-subheader>
          <img class="avatar-preview shadowed pt-3" :src="subject.avatar_url" :alt="subject.username"/>
          <p v-if="subject.avatar_url.indexOf('gravatar') > -1">Default avatars provided by <a
              href="http://en.gravatar.com/">Gravatar</a></p>
        </v-card-text>
      </v-card>
    </v-flex>
    <v-flex d-flex xs12 sm6 lg3>
      <ac-uppy-file
          :endpoint="url"
          :success="subjectHandler.updateX"
          label="Upload a new Avatar"
      ></ac-uppy-file>
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import Subjective from '@/mixins/subjective'
import AcUppyFile from '@/components/fields/AcUppyFile.vue'

  @Component({
    components: {AcUppyFile},
  })
export default class Avatar extends mixins(Viewer, Subjective) {
  private get url() {
    return `/api/profiles/v1/account/${this.subject && this.subject.username}/avatar/`
  }
}
</script>

<style scoped>

</style>
