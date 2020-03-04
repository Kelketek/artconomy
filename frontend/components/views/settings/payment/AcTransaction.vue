<template>
  <v-list-item>
    <v-list-item-content>
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
    </v-list-item-content>
    <v-list-item-action>
      <v-btn icon text @click="showDetails = true">
        <v-icon>more_horiz</v-icon>
      </v-btn>
    </v-list-item-action>
    <v-dialog v-model="showDetails" max-width="800px">
      <v-toolbar flat dark color="secondary" :dense="$vuetify.breakpoint.mdAndUp">
        <v-toolbar-title><slot name="title">Transaction Details</slot></v-toolbar-title>
        <v-spacer/>
        <v-btn icon @click.native="showDetails = false" dark class="dialog-closer">
          <v-icon>close</v-icon>
        </v-btn>
      </v-toolbar>
      <v-card>
        <v-card-text>
          <v-row no-gutters  >
            <v-col cols="6">TXN ID: {{transaction.id}}</v-col>
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
            <v-col cols="6" v-if="transaction.card">Card: {{issuer.name}} x{{transaction.card.last_four}}</v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="text-right">
          <v-spacer /><v-btn color="primary" @click.stop="showDetails=false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-list-item>
</template>

<script lang="ts">
import Subjective from '@/mixins/subjective'
import Component, {mixins} from 'vue-class-component'
import Transaction from '@/types/Transaction'
import {Prop} from 'vue-property-decorator'
import {User} from '@/store/profiles/types/User'
import Formatting from '@/mixins/formatting'
import {ISSUERS} from '@/lib/lib'

@Component
export default class AcTransaction extends mixins(Subjective, Formatting) {
    @Prop({required: true})
    public transaction!: Transaction

    @Prop({required: true})
    public currentAccount!: number

    public showDetails = false

    public STATUS_COMMENTS = {
      0: '',
      1: '(Failed)',
      2: '(Pending)',
    }

    public STATUSES = {
      0: 'Success',
      1: 'Failure',
      2: 'Pending',
    }

    public CATEGORY_TYPES = {
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
    }

    public ACCOUNT_TYPES = {
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
      // @ts-ignore
      return ISSUERS[this.transaction.card.type]
    }
    public displayName(target: User|null) {
      if (!target) {
        return '[Artconomy]'
      } else {
        return target.username
      }
    }
}
</script>
