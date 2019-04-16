<template>
  <fragment>
    <v-toolbar :dense="$vuetify.breakpoint.smAndDown">
      <slot name="avatar">
        <ac-avatar :username="username" :show-name="false"></ac-avatar>
        <v-toolbar-title>{{subjectHandler.displayName}}</v-toolbar-title>
      </slot>
      <v-spacer></v-spacer>
      <v-toolbar-items v-if="!$vuetify.breakpoint.xs">
        <slot></slot>
      </v-toolbar-items>
    </v-toolbar>
    <v-toolbar v-if="$vuetify.breakpoint.xs" dense class="subjective-mini-buttons" height="32px">
      <slot></slot>
    </v-toolbar>
  </fragment>
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
import Component, {mixins} from 'vue-class-component'
import AcAvatar from '../AcAvatar.vue'
import Subjective from '../../mixins/subjective'
import {Fragment} from 'vue-fragment'

  @Component({
    components: {AcAvatar, Fragment},
  })
export default class AcSubjectiveToolbar extends mixins(Subjective) {
}
</script>
