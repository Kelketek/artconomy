<template>
  <div :id="id"></div>
</template>

<script setup lang="ts">
import {useSubject} from '@/mixins/subjective.ts'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {computed} from 'vue'
import {useRoute} from 'vue-router'

const props = withDefaults(defineProps<SubjectiveProps & {isPrivate?: boolean, isProtected?: boolean}>(), {isPrivate: false, isProtected: false})
const route = useRoute()
const subjectValues = useSubject({ props, privateView: props.isPrivate, controlPowers: ['administrate_users']})
defineExpose(subjectValues)

const id = computed(() => {
  if (route.name) {
    return (String(route.name) + '-component').toLowerCase()
  }
  return 'subjective-component'
})
</script>
