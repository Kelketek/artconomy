<template>
  <v-row id="avatar-settings">
    <v-col class="text-center" cols="12" sm="3" lg="3" offset-sm="2" offset-lg="3" align-self="center">
      <v-card>
        <v-card-text>
          <v-subheader>Current Avatar</v-subheader>
          <img class="avatar-preview shadowed pt-3" :src="subject.avatar_url" :alt="subject.username"/>
          <p v-if="subject.avatar_url.indexOf('gravatar') > -1">Default avatars provided by <a
              href="http://en.gravatar.com/">Gravatar</a></p>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" sm="6" lg="3">
      <ac-uppy-file
          uppy-id="uppy-avatar"
          :endpoint="url"
          :success="subjectHandler.updateX"
          label="Upload a new Avatar"
      />
    </v-col>
  </v-row>
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
    return `/api/profiles/account/${this.subject && this.subject.username}/avatar/`
  }

  public created() {
    this.$listenForSingle('uppy-avatar')
  }
}
</script>

<style scoped>

</style>
