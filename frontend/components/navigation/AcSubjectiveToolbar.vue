<template>
  <v-toolbar :dense="true" color="black" class="subjective-toolbar">
    <slot name="avatar">
      <ac-avatar :username="username" :show-name="false" class="ml-3" />
      <v-toolbar-title class="ml-1">
        <ac-link :to="profileLink(subject)">{{subjectHandler.displayName}}</ac-link>
      </v-toolbar-title>
    </slot>
    <v-spacer/>
    <v-toolbar-items v-if="!display.xs.value">
      <slot/>
    </v-toolbar-items>
  </v-toolbar>
  <v-toolbar v-if="display.xs.value" dense class="subjective-mini-buttons" height="32px">
    <slot/>
  </v-toolbar>
</template>

<style>
.subjective-mini-buttons .v-toolbar__content {
  justify-content: center; }
.subjective-mini-buttons .v-toolbar__content .v-btn {
  padding: 0 4px;
  font-size: 80%; }
.subjective-mini-buttons .v-toolbar__content .v-btn .v-icon--left {
  margin-right: 4px; }
</style>

<script setup lang="ts">
import AcAvatar from '../AcAvatar.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useSubject} from '@/mixins/subjective.ts'
import {useDisplay} from 'vuetify'

import {profileLink} from '@/lib/otherFormatters.ts'

const props = defineProps<SubjectiveProps>()
const {subjectHandler, subject} = useSubject(props)
const display = useDisplay()
// @ts-ignore
window.display = display
</script>
