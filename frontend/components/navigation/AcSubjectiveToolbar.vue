<template>
  <v-toolbar :dense="true" color="black">
    <slot name="avatar">
      <ac-avatar :username="username" :show-name="false" class="ml-3" />
      <v-toolbar-title class="ml-1">
        <ac-link :to="profileLink(subject)">{{subjectHandler.displayName}}</ac-link>
      </v-toolbar-title>
    </slot>
    <v-spacer/>
    <v-toolbar-items v-if="!$vuetify.display.xs">
      <slot/>
    </v-toolbar-items>
  </v-toolbar>
  <v-toolbar v-if="$vuetify.display.xs" dense class="subjective-mini-buttons" height="32px">
    <slot/>
  </v-toolbar>
</template>

<style lang="sass">
.subjective-mini-buttons
  .v-toolbar__content
    justify-content: center

    .v-btn
      padding: 0 4px
      font-size: 80%

      .v-icon--left
        margin-right: 4px
</style>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import AcAvatar from '../AcAvatar.vue'
import Subjective from '../../mixins/subjective'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting'

@Component({
  components: {
    AcLink,
    AcAvatar,
  },
})
class AcSubjectiveToolbar extends mixins(Subjective, Formatting) {
}

export default toNative(AcSubjectiveToolbar)
</script>
