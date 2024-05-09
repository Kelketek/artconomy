<template>
  <v-container fluid>
    <ac-subjective-product-list :username="username"/>
  </v-container>
</template>

<script setup lang="ts">
import AcSubjectiveProductList from '@/components/views/store/AcSubjectiveProductList.vue'
import SubjectiveProps from '@/types/SubjectiveProps.ts'

const props = defineProps<SubjectiveProps>()
</script>
