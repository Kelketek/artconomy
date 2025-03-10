<template>
  <div v-if="flag !== null">
    <v-alert
      v-if="flag == ReportFlags.COPYRIGHT_CLAIMED"
      type="warning"
    >
      Copyright claims must be made via DMCA request, with procedure outlined in the
      <router-link :to="{name: 'TermsOfService'}">
        Terms of Service
      </router-link>. You may use
      this form for any additional questions, but reports cannot be made here.
    </v-alert>
    <v-alert type="info">
      <p>Please check the description below to verify this is the correct category:</p>
      <div v-html="flagDetails" />
    </v-alert>
  </div>
</template>

<script setup lang="ts">
import {ReportFlags} from '@/types/enums/ReportFlags.ts'
import type {ReportFlagsValue} from '@/types/main.d.ts'
import {computed} from 'vue'

const props = defineProps<{flag: ReportFlagsValue|null}>()
const explanations: Record<ReportFlagsValue, string> = {
  [ReportFlags.ILLEGAL_CONTENT]: '<p>Illegal content is content or services which are illegal in the United States of America generally or Texas in particular. This is separate from copyright claims, which have their own procedure.</a>',
  [ReportFlags.EXPLICIT_PHOTOGRAPHS]: '<p>This content is explicit content of real persons, or is of a render quality easily confused with real persons, such as AI-generated explicit images or detailed 3D renderings.</p>',
  [ReportFlags.COPYRIGHT_CLAIMED]: '<p>You are the copyright holder of this content (or their legal representative) and you have questions about the takedown procedure.</p>',
  [ReportFlags.SPAM_OR_NOT_ART]: '<p>This content does not appear to be an earnest art submission, or it is repetitive content. It is something other than art, such as datasets, compiled applications other than games, or something otherwise not reasonably understood as art. Alternatively, it is a submission within a large gallery of AI-generated work, or an advertisement not pertinent to the work/availability of the artist in question, and not reasonably understood to be part of a design portfolio.</p>',
  [ReportFlags.IMPROPERLY_RATED]: '<p>This content is improperly rated-- such as adult content being rated as general content.</p>',
  [ReportFlags.IMPROPERLY_TAGGED]: '<p>This content is missing critical tags that would allow it to be filtered by those uninterested in its subject-matter, or it has tags irrelevant to its subject-matter.</p>',
}
const flagDetails = computed(() => props.flag === null ? '' : explanations[props.flag])
</script>
