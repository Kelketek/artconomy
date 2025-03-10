<template>
  <v-app>
    <v-main>
      <ac-new-submission
        ref="submissionForm"
        v-model="showUpload"
        title="Sharable thing!"
        :username="username"
        :allow-multiple="allowMultiple"
      />
    </v-main>
  </v-app>
</template>
<script setup lang="ts">
import {useUpload} from '@/mixins/upload.ts'
import AcNewSubmission from '@/components/AcNewSubmission.vue'
import type {SubjectiveProps} from '@/types/main'

const props = withDefaults(defineProps<SubjectiveProps & {allowMultiple?: boolean}>(), {allowMultiple: false})
const {showUpload} = useUpload()
showUpload.value = true
</script>
