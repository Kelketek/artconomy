<template>
  <v-list-item>
    <div>
      <v-list-item-title>
        {{ STATUS_COMMENTS[transaction.status] }} {{ amount }}
      </v-list-item-title>
      <v-list-item-subtitle v-if="objective">
        {{ displayName(transaction.payer) }} ([{{ ACCOUNT_TYPES[transaction.source] }}]) to {{ displayName(transaction.payee) }} ([{{ ACCOUNT_TYPES[transaction.destination] }}])
      </v-list-item-subtitle>
      <v-list-item-subtitle v-else>
        <span v-if="outbound">to</span>
        <span v-else>from</span>&nbsp;
        {{ displayName(other) }}&nbsp;
        ({{ ACCOUNT_TYPES[otherAccount] }})
      </v-list-item-subtitle>
      <v-list-item-subtitle>
        {{ formatDateTime(transaction.created_on) }}
      </v-list-item-subtitle>
    </div>
    <template #append>
      <v-btn
        icon
        variant="text"
        aria-label="Actions"
        @click="showDetails = true"
      >
        <v-icon :icon="mdiDotsHorizontal" />
      </v-btn>
    </template>
    <v-dialog
      v-model="showDetails"
      max-width="800px"
      :attach="modalTarget"
    >
      <v-toolbar
        flat
        dark
        color="secondary"
        :dense="mdAndUp"
      >
        <v-toolbar-title>
          <slot name="title">
            Transaction Details
          </slot>
        </v-toolbar-title>
        <v-spacer />
        <v-btn
          icon
          variant="flat"
          dark
          class="dialog-closer"
          @click="showDetails = false"
        >
          <v-icon :icon="mdiClose" />
        </v-btn>
      </v-toolbar>
      <v-card>
        <v-card-text>
          <v-row no-gutters>
            <v-col cols="6">
              TXN ID:
              <ac-link
                :to="transactionLink"
                :new-tab="true"
              >
                {{ transaction.id }}
              </ac-link>
            </v-col>
            <v-col cols="6">
              Category: {{ CATEGORY_TYPES[transaction.category] }}
            </v-col>
            <v-col cols="6">
              Status: {{ STATUSES[transaction.status] }}
            </v-col>
            <v-col cols="6">
              Payer: {{ displayName(transaction.payer) }}
            </v-col>
            <v-col cols="6">
              Payee: {{ displayName(transaction.payee) }}
            </v-col>
            <v-col cols="6">
              <span v-if="transaction.remote_id">Remote TXN ID: {{ transaction.remote_id }}</span>
            </v-col>
            <v-col cols="6">
              <strong>
                <span v-if="transaction.finalized_on">Finalized on {{ formatDateTime(transaction.finalized_on) }}</span>
                <span v-else>Not Finalized</span>
              </strong>
            </v-col>
            <v-col
              v-if="transaction.card"
              cols="6"
            >
              Card: {{ issuer!.name }} x{{ transaction.card.last_four }}
            </v-col>
            <v-col cols="6">
              <v-list-subheader>Refs:</v-list-subheader>
              <ul>
                <li
                  v-for="transactionRef, index in transaction.targets"
                  :key="index"
                >
                  <ac-link :to="transactionRef.link">
                    {{ transactionRef.model }} #{{ transactionRef.id }}
                  </ac-link>
                </li>
              </ul>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="text-right">
          <v-spacer />
          <v-btn
            color="primary"
            @click.stop="showDetails=false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-list-item>
</template>

<script setup lang="ts">
import AcLink from '@/components/wrappers/AcLink.vue'
import {ISSUERS} from '@/components/views/settings/payment/issuers.ts'
import {mdiClose, mdiDotsHorizontal} from '@mdi/js'
import {computed, ref} from 'vue'
import {useViewer} from '@/mixins/viewer.ts'
import {formatDateTime} from '@/lib/otherFormatters.ts'
import {useTargets} from '@/plugins/targets.ts'
import {useDisplay} from 'vuetify'
import type {
  AccountTypeValue,
  Transaction,
  TransactionCategoryValue,
  TransactionStatusValue,
} from '@/types/main'
import {RelatedUser} from '@/store/profiles/types/main'


const props = withDefaults(defineProps<{username: string|null, transaction: Transaction, asAccount: number, objective?: boolean}>(), {objective: false})

const {isSuperuser} = useViewer()
const {modalTarget} = useTargets()
const {mdAndUp} = useDisplay()

const showDetails = ref(false)

const STATUS_COMMENTS: Record<TransactionStatusValue, string> = {
  0: '',
  1: '(Failed)',
  2: '(Pending)',
}

const STATUSES: Record<TransactionStatusValue, string> = {
  0: 'Success',
  1: 'Failure',
  2: 'Pending',
}

const CATEGORY_TYPES: Record<TransactionCategoryValue, string> = {
  400: 'Artconomy Service Fee',
  401: 'Escrow hold',
  402: 'Escrow release',
  403: 'Escrow refund',
  404: 'Subscription dues',
  405: 'Refund for subscription dues',
  406: 'Cash withdrawal',
  407: 'Cash deposit',
  408: 'Third party fee',
  409: 'Premium service bonus',
  410: 'Internal Transfer',
  411: 'Third party refund',
  412: 'Error correction',
  413: 'Table Handling Fee',
  414: 'Taxes',
  415: 'Extra Item',
  416: 'Manual Payout',
  417: 'Payout Reversal',
  418: 'Processing Fee',
  419: 'Tip',
}

const ACCOUNT_TYPES: Record<AccountTypeValue, string> = {
  300: 'Credit Card',
  301: 'Bank Account',
  302: 'Escrow',
  303: 'Finalized Earnings, available for withdraw',
  304: 'Bonus reserve',
  305: 'Unannotated earnings',
  306: 'Card transaction fees',
  307: 'Other card fees',
  308: 'ACH Transaction fees',
  309: 'Other ACH fees',
  310: 'Tax staging',
  311: 'Taxes',
  313: 'Fund',
  407: 'Cash deposit',
}

const isPayer = computed(() => {
  if (props.username === null && props.transaction.payer === null) {
    return true
  }
  return (props.transaction.payer && props.transaction.payer.username === props.username)
})

const isPayee = computed(() => {
  if (props.username === null && props.transaction.payee === null) {
    return true
  }
  return (props.transaction.payee && props.transaction.payee.username === props.username)
})

const outbound = computed(() => {
  return isPayer.value && ((!isPayee.value) || (props.transaction.destination !== props.asAccount))
})

const other = computed(() => {
  if (outbound.value) {
    return props.transaction.payee
  }
  return props.transaction.payer
})

const otherAccount = computed(() => {
  if (outbound.value) {
    return props.transaction.destination
  }
  return props.transaction.source
})

const amount = computed(() => {
  if (outbound.value) {
    return `-$${props.transaction.amount}`
  }
  return `$${props.transaction.amount}`
})

const issuer = computed(() => {
  /* istanbul ignore if */
  if (!props.transaction.card) {
    return null
  }
  return ISSUERS[props.transaction.card.type]
})

const transactionLink = computed(() => {
  if (!isSuperuser.value) {
    return null
  }
  return `/admin/sales/transactionrecord/${props.transaction.id}/`
})

const displayName = (target: RelatedUser | null) => {
  if (!target) {
    return '[Artconomy]'
  } else {
    return target.username
  }
}
</script>
