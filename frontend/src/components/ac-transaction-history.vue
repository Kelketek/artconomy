<template>
  <div>
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-purchases">
        <v-icon>shopping_cart</v-icon> Purchases
      </v-tab>
      <v-tab href="#tab-escrow">
       <v-icon>lock</v-icon> Escrow
      </v-tab>
      <v-tab href="#tab-available">
        <v-icon>attach_money</v-icon> Available
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item value="tab-purchases">
        <ac-transaction-listing :endpoint="`${url}purchases/`" :username="username" />
      </v-tab-item>
      <v-tab-item value="tab-escrow">
        <ac-transaction-listing :endpoint="`${url}escrow/`" :username="username" :escrow="true" />
      </v-tab-item>
      <v-tab-item value="tab-available">
        <ac-transaction-listing :endpoint="`${url}available/`" :username="username" />
      </v-tab-item>
    </v-tabs-items>
  </div>
</template>

<script>
  import AcTransaction from './ac-transaction'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import { paramHandleMap } from '../lib'
  import AcTransactionListing from './ac-transaction-listing'

  export default {
    components: {
      AcTransactionListing,
      AcTransaction},
    mixins: [Viewer, Perms],
    props: ['endpoint'],
    data () {
      return {
        url: this.endpoint
      }
    },
    computed: {
      tab: paramHandleMap('tertiaryTabName', undefined, ['tab-purchases', 'tab-escrow', 'tab-available'], 'tab-purchases')
    }
  }
</script>