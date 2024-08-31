<template>
  <v-toolbar density="compact" color="black" class="subjective-toolbar">
    <slot name="avatar">
      <ac-avatar :username="username" :show-name="false" class="ml-3" />
      <v-toolbar-title class="ml-1">
        <ac-link :to="profileLink(subject)">{{subjectHandler.displayName}}</ac-link>
      </v-toolbar-title>
    </slot>
    <v-spacer/>
    <v-toolbar-items v-if="!xs">
      <slot/>
    </v-toolbar-items>
  </v-toolbar>
  <v-toolbar v-if="xs" :dense="true" class="subjective-mini-buttons" density="compact">
    <v-toolbar-items>
      <slot/>
    </v-toolbar-items>
  </v-toolbar>
</template>

<style>
</style>

<script setup lang="ts">
import AcAvatar from '../AcAvatar.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useSubject} from '@/mixins/subjective.ts'
import {useDisplay} from 'vuetify'

import {profileLink} from '@/lib/otherFormatters.ts'

const props = defineProps<SubjectiveProps>()
const {subjectHandler, subject} = useSubject({ props })
const {xs} = useDisplay()
</script>
