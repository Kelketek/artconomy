<template>
  <ac-load-section :controller="subjectHandler.user">
    <template v-slot:default>
      <ac-site-financials v-if="subject!.is_superuser"/>
      <ac-tax-reports :username="username"/>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcSiteFinancials from '@/components/views/reports/AcSiteFinancials.vue'
import AcTaxReports from '@/components/views/reports/AcTaxReports.vue'

@Component({
  components: {
    AcTaxReports,
    AcSiteFinancials,
    AcLoadSection,
  },
})
class Reports extends mixins(Subjective) {
  public privateView = true
}

export default toNative(Reports)
</script>
