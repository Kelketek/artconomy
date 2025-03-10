<template>
  <div :id="id" />
</template>

<script setup lang="ts">
import {useSubject} from '@/mixins/subjective.ts'
import {computed} from 'vue'
import {useRoute} from 'vue-router'
import type {SubjectiveProps} from '@/types/main'
import {StaffPower} from '@/store/profiles/types/main'

const props = withDefaults(defineProps<SubjectiveProps & {isPrivate?: boolean, isProtected?: boolean, hasControlPowers?: StaffPower[]}>(), {isPrivate: false, isProtected: false, hasControlPowers: () => [] as StaffPower[]})
const route = useRoute()
const subjectValues = useSubject({ props, privateView: props.isPrivate, controlPowers: props.hasControlPowers })
defineExpose(subjectValues)

const id = computed(() => {
  if (route.name) {
    return (String(route.name) + '-component').toLowerCase()
  }
  return 'subjective-component'
})
</script>
