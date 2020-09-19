<template>
  <v-tooltip top>
    <template v-slot:activator="{ on }"><span v-on="on"><ac-link :to="profileLink">@{{username}}</ac-link></span></template>
    <ac-avatar :username="username" :user="subject" v-if="subject" />
  </v-tooltip>
</template>

<script lang="ts">
import Subjective from '../mixins/subjective'
import Component, {mixins} from 'vue-class-component'
import AcAvatar from './AcAvatar.vue'
import {profileLink} from '@/lib/lib'
import AcLink from './wrappers/AcLink.vue'

@Component({
  components: {AcLink, AcAvatar},
})
export default class InlineAvatar extends mixins(Subjective) {
  missingOk = true

  public get profileLink() {
    if (this.subject) {
      return profileLink(this.subject)
    }
  }
}
</script>
