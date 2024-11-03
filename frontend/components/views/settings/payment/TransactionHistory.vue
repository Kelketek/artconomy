<template>
  <v-row no-gutters>
    <v-col cols="12" v-if="subject!.artist_mode">
      <ac-bound-field
          :field="transactionFilter.fields.account"
          field-type="v-select"
          :items="[{title: 'Purchases', value: 300}, {title: 'Escrow', value: 302}, {title: 'Holdings', value: 303}]"
          label="Account"
      />
    </v-col>
    <v-col cols="12">
      <ac-paginated :list="transactions">
        <template v-slot:default>
          <v-row>
            <v-col cols="12">
              <v-list three-line>
                <template v-for="transaction, index in transactions.list" :key="transaction.x!.id">
                  <ac-transaction :transaction="transaction.x!" :username="username"
                                  :current-account="transactionFilter.fields.account.value"/>
                  <v-divider v-if="index + 1 < transactions.list.length" :key="index"/>
                </template>
              </v-list>
            </v-col>
          </v-row>
        </template>
      </ac-paginated>
    </v-col>
    <v-col cols="12" v-if="!purchaseList">
      <ac-load-section :controller="summary">
        <template v-slot:default>
          <strong>Working Balance:</strong> ${{summary.x!.available}}<br/>
          <span v-if="!escrowList"><strong>Pending Changes:</strong> ${{summary.x!.pending}}</span>
        </template>
      </ac-load-section>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import {useSubject} from '@/mixins/subjective.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcTransaction from '@/components/views/settings/payment/AcTransaction.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {flatten} from '@/lib/lib.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {computed, watch} from 'vue'
import type {Balance, SubjectiveProps, Transaction} from '@/types/main'
import {RawData} from '@/store/forms/types/main'

const props = defineProps<SubjectiveProps>()

const {subject} = useSubject({ props })

const transactionFilter = useForm(`transactions_form__${flatten(props.username)}`, {
  endpoint: '',
  fields: {account: {value: 300}},
})
const transactions = useList<Transaction>(`transactions__${flatten(props.username)}`, {
  endpoint: `/api/sales/account/${props.username}/transactions/`,
  params: transactionFilter.rawData,
})
transactions.firstRun()
const summary = useSingle<Balance>(flatten(`account_summary__${props.username}`), {
  endpoint: `/api/sales/account/${props.username}/account-status/`,
  params: transactionFilter.rawData,
})
summary.get()

const purchaseList = computed(() => {
  return transactionFilter.fields.account.value === 300
})

const escrowList = computed(() => {
  return transactionFilter.fields.account.value === 302
})

watch(() => transactionFilter.rawData, (data: RawData) => {
  transactions.params = data
  transactions.reset()
  summary.ready = false
  summary.fetching = false
  summary.setX(null)
  summary.params = data
  summary.get()
})
</script>
