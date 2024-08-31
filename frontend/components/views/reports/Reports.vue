<template>
  <ac-load-section :controller="subjectHandler.user">
    <template v-slot:default>
      <ac-site-financials v-if="subject!.is_superuser"/>
      <ac-tax-reports :username="username"/>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import {useSubject} from '@/mixins/subjective.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcSiteFinancials from '@/components/views/reports/AcSiteFinancials.vue'
import AcTaxReports from '@/components/views/reports/AcTaxReports.vue'
import SubjectiveProps from '@/types/SubjectiveProps.ts'


const props = defineProps<SubjectiveProps>()
const {subject, subjectHandler} = useSubject({ props, privateView: true })
</script>
