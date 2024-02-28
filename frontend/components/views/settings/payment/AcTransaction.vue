<template>
  <v-list-item>
    <div>
      <v-list-item-title>
        {{STATUS_COMMENTS[transaction.status]}} ${{amount.toFixed(2)}}
      </v-list-item-title>
      <v-list-item-subtitle>
        <span v-if="outbound">to</span>
        <span v-else>from</span>&nbsp;
        {{displayName(other)}}&nbsp;
        ({{ACCOUNT_TYPES[otherAccount]}})
      </v-list-item-subtitle>
      <v-list-item-subtitle>
        {{formatDateTime(transaction.created_on)}}
      </v-list-item-subtitle>
    </div>
    <template v-slot:append>
      <v-btn icon variant="text" @click="showDetails = true" aria-label="Actions">
        <v-icon icon="mdi-dots-horizontal"/>
      </v-btn>
    </template>
    <v-dialog v-model="showDetails" max-width="800px" :attach="$modalTarget">
      <v-toolbar flat dark color="secondary" :dense="$vuetify.display.mdAndUp">
        <v-toolbar-title>
          <slot name="title">Transaction Details</slot>
        </v-toolbar-title>
        <v-spacer/>
        <v-btn icon @click="showDetails = false" variant="flat" dark class="dialog-closer">
          <v-icon icon="mdi-close"/>
        </v-btn>
      </v-toolbar>
      <v-card>
        <v-card-text>
          <v-row no-gutters>
            <v-col cols="6">TXN ID:
              <ac-link :to="transactionLink" :new-tab="true">{{transaction.id}}</ac-link>
            </v-col>
            <v-col cols="6">Category: {{CATEGORY_TYPES[transaction.category]}}</v-col>
            <v-col cols="6">Status: {{STATUSES[transaction.status]}}</v-col>
            <v-col cols="6">Payer: {{displayName(transaction.payer)}}</v-col>
            <v-col cols="6">Payee: {{displayName(transaction.payee)}}</v-col>
            <v-col cols="6"><span v-if="transaction.remote_id">Remote TXN ID: {{transaction.remote_id}}</span></v-col>
            <v-col cols="6">
              <strong>
                <span v-if="transaction.finalized_on">Finalized on {{formatDateTime(transaction.finalized_on)}}</span>
                <span v-else>Not Finalized</span>
              </strong>
            </v-col>
            <v-col cols="6" v-if="transaction.card">Card: {{issuer!.name}} x{{transaction.card.last_four}}</v-col>
            <v-col cols="6">
              <v-list-subheader>Refs:</v-list-subheader>
              <ul>
                <li v-for="ref, index in transaction.targets" :key="index">
                  <ac-link :to="ref.link">{{ref.model}} #{{ref.id}}</ac-link>
                </li>
              </ul>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="text-right">
          <v-spacer/>
          <v-btn color="primary" @click.stop="showDetails=false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-list-item>
</template>

<script lang="ts">
import Subjective from '@/mixins/subjective.ts'
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import Transaction from '@/types/Transaction.ts'
import {User} from '@/store/profiles/types/User.ts'
import Formatting from '@/mixins/formatting.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'
import {TransactionCategory} from '@/types/TransactionCategory.ts'
import {TransactionStatus} from '@/types/TransactionStatus.ts'
import {AccountType} from '@/types/AccountType.ts'
import {ISSUERS} from '@/components/views/settings/payment/issuers.ts'

@Component({
  components: {AcLink},
})
class AcTransaction extends mixins(Subjective, Formatting) {
  @Prop({required: true})
  public transaction!: Transaction

  @Prop({required: true})
  public currentAccount!: number

  public showDetails = false

  public STATUS_COMMENTS: Record<TransactionStatus, string> = {
    0: '',
    1: '(Failed)',
    2: '(Pending)',
  }

  public STATUSES: Record<TransactionStatus, string> = {
    0: 'Success',
    1: 'Failure',
    2: 'Pending',
  }

  public CATEGORY_TYPES: Record<TransactionCategory, string> = {
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

  public ACCOUNT_TYPES: Record<AccountType, string> = {
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
    407: 'Cash deposit',
  }

  public get isPayer() {
    const subject = this.subject as User
    return (this.transaction.payer && this.transaction.payer.username === subject.username)
  }

  public get isPayee() {
    const subject = this.subject as User
    return (this.transaction.payee && this.transaction.payee.username === subject.username)
  }

  public get outbound() {
    return this.isPayer && ((!this.isPayee) || (this.transaction.destination !== this.currentAccount))
  }

  public get other() {
    if (this.outbound) {
      return this.transaction.payee
    }
    return this.transaction.payer
  }

  public get otherAccount() {
    if (this.outbound) {
      return this.transaction.destination
    }
    return this.transaction.source
  }

  public get amount() {
    if (this.outbound) {
      return 0 - this.transaction.amount
    }
    return this.transaction.amount
  }

  public get issuer() {
    /* istanbul ignore if */
    if (!this.transaction.card) {
      return null
    }
    return ISSUERS[this.transaction.card.type]
  }

  public get transactionLink() {
    if (!this.isSuperuser) {
      return null
    }
    return `/admin/sales/transactionrecord/${this.transaction.id}/`
  }

  public displayName(target: RelatedUser | null) {
    if (!target) {
      return '[Artconomy]'
    } else {
      return target.username
    }
  }
}

export default toNative(AcTransaction)
</script>
