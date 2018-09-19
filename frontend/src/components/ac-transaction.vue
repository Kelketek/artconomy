<template>
  <v-list-tile>
    <v-list-tile-content>
      <v-list-tile-title>
        {{failedIndicator}} {{sign}}${{transaction.amount}} <router-link :to="link" v-if="link">{{action}}</router-link><span v-else>{{action}}</span>
      </v-list-tile-title>
      <v-list-tile-sub-title>
        {{direction }} {{other.username}}
      </v-list-tile-sub-title>
      <v-list-tile-sub-title>
        {{formatDateTime(transaction.created_on)}}
      </v-list-tile-sub-title>
    </v-list-tile-content>
    <v-list-tile-action>
      <v-icon @click="showDetails = true">more_horiz</v-icon>
    </v-list-tile-action>
    <v-dialog v-model="showDetails" max-width="500px">
      <v-card>
        <v-card-title>
          Transaction Details
        </v-card-title>
        <v-card-text>
          <v-layout row wrap>
            <v-flex xs6>Transaction type: <span v-if="isPayer || isEscrowFor">{{paidAction}}</span></v-flex>
            <v-flex xs6>Status: {{status}}</v-flex>
            <v-flex xs6>Payer: {{payer.username}}</v-flex>
            <v-flex xs6>Payee: {{payee.username}}</v-flex>
            <v-flex xs6>TXN ID: {{transaction.id}}</v-flex>
            <v-flex xs6>Remote TXN ID: {{transaction.txn_id}}</v-flex>
            <v-flex xs6><strong><span v-if="transaction.finalized">Finalized</span><span v-else>Not Finalized</span></strong></v-flex>
            <v-flex xs6 v-if="transaction.card">Card: {{issuer.name}} x{{transaction.card.last_four}}</v-flex>
          </v-layout>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" flat @click.stop="showDetails=false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-list-tile>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import { ACCOUNT_TYPES, formatDateTime, ISSUERS } from '../lib'

  const TYPES = {
    SALE: 200,
    DISBURSEMENT_SENT: 201,
    DISBURSEMENT_RETURNED: 202,
    DISBURSEMENT_FAILED: 203,
    REFUND: 204,
    TRANSFER: 205
  }

  export default {
    props: ['transaction', 'escrow'],
    mixins: [Viewer, Perms],
    data () {
      return {
        showDetails: false
      }
    },
    methods: {
      formatDateTime: formatDateTime
    },
    computed: {
      isPayer () {
        return this.transaction.payer && this.transaction.payer.username === this.user.username
      },
      isPayee () {
        return this.transaction.payee && this.transaction.payee.username === this.user.username
      },
      isEscrowFor () {
        return this.transaction.escrow_for && this.transaction.escrow_for.username === this.user.username
      },
      other () {
        if (this.transaction.type === TYPES.DISBURSEMENT_SENT || this.transaction.type === TYPES.DISBURSEMENT_FAILED) {
          if (this.transaction.target === null) {
            return {username: '[Unknown]'}
          }
          let bank = ACCOUNT_TYPES[this.transaction.target.type] + ' x' + this.transaction.target.last_four + ''
          return {
            username: bank
          }
        }
        if (this.transaction.payer === null && this.escrow) {
          return {username: 'Available'}
        }
        if (this.transaction.escrow_for !== null && this.escrow) {
          return this.transaction.payer
        }
        if (this.transaction.payer === null && !this.escrow) {
          return {username: 'Escrow'}
        }
        if (this.transaction.payee === null && this.transaction.escrow_for) {
          return this.transaction.escrow_for
        }
        if (this.transaction.payee === null) {
          return {username: 'Artconomy'}
        }
        if (this.transaction.payee) {
          return this.transaction.payee
        }
        return {username: 'Unknown'}
      },
      payer () {
        if (this.transaction.type === TYPES.DISBURSEMENT_SENT || this.transaction.type === TYPES.DISBURSEMENT_FAILED) {
          if (this.transaction.target === null) {
            return {username: '[Unknown]'}
          }
          let bank = ACCOUNT_TYPES[this.transaction.target.type] + ' x' + this.transaction.target.last_four + ''
          return {
            username: bank
          }
        } else if (this.transaction.payer) {
          return this.transaction.payer
        } else {
          return {username: 'Artconomy'}
        }
      },
      sign () {
        if (this.escrow && this.isPayee) {
          return '-'
        }
        if (this.isPayer) {
          return '-'
        }
        return ''
      },
      direction () {
        if (this.sign === '-') {
          return 'to'
        } else {
          return 'from'
        }
      },
      payee () {
        if (this.transaction.type === TYPES.DISBURSEMENT_SENT || this.transaction.type === TYPES.DISBURSEMENT_FAILED) {
          if (this.transaction.target === null) {
            return {username: '[Unknown]'}
          }
          let bank = ACCOUNT_TYPES[this.transaction.target.type] + ' x' + this.transaction.target.last_four + ''
          return {
            username: bank
          }
        }
        if (this.transaction.escrow_for !== null) {
          return {username: 'Escrow'}
        } else if (this.transaction.payee === null) {
          return {username: 'Artconomy'}
        } else {
          return this.transaction.payee
        }
      },
      paidAction () {
        if (this.transaction.type === TYPES.SALE) {
          if (this.transaction.escrow_for === null) {
            return 'Service Payment to Artconomy'
          }
          if (this.transaction.escrow_for.username === this.username) {
            return 'Escrow hold: Sale #' + this.transaction.target.id
          } else {
            return 'Order #' + this.transaction.target.id
          }
        } else if (this.transaction.type === TYPES.DISBURSEMENT_SENT) {
          return 'Withdraw'
        } else if (this.transaction.type === TYPES.DISBURSEMENT_RETURNED) {
          return 'Returned funds from failed withdraw'
        } else if (this.transaction.type === TYPES.REFUND) {
          return 'Refund'
        } else if (this.transaction.type === TYPES.TRANSFER) {
          if (this.transaction.payee === null) {
            return 'Fee payment'
          } else {
            return 'Transfer'
          }
        } else {
          return 'Unknown pmnt type ' + this.transaction.type
        }
      },
      failedIndicator () {
        if (this.transaction.status) {
          return '(FAILED)'
        } else {
          return ''
        }
      },
      receivedAction () {
        if (this.transaction.type === TYPES.TRANSFER) {
          if (this.transaction.payer === null) {
            return 'Payout: Sale #' + this.transaction.target.id
          } else {
            return 'Transfer'
          }
        }
        return 'Unknown rcpt type ' + this.transaction.type
      },
      link () {
        if (!this.transaction.target) {
          return ''
        }
        if (this.transaction.type === TYPES.SALE) {
          // Check for Escrow here in the case the user purchases something from themselves.
          if (this.transaction.payer.username === this.username && !this.escrow) {
            return `/orders/${this.username}/order/${this.transaction.target.id}`
          }
          if (this.transaction.escrow_for.username === this.username) {
            return `/sales/${this.username}/sale/${this.transaction.target.id}`
          }
        }
        if (this.transaction.type === TYPES.TRANSFER) {
          return `/sales/${this.username}/sale/${this.transaction.target.id}`
        }
      },
      action () {
        if (this.isPayer || this.isEscrowFor) {
          return this.paidAction
        } else {
          return this.receivedAction
        }
      },
      status () {
        if (this.transaction.status) {
          return 'FAILED'
        } else if (!this.transaction.finalized) {
          return 'PENDING'
        } else {
          return 'SUCCESS'
        }
      },
      issuer () {
        return ISSUERS[this.transaction.card.card_type]
      }
    }
  }
</script>