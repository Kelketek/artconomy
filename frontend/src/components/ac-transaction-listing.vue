<template>
  <v-card v-if="growing !== null" class="text-xs-center">
    <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" :total-visible="totalVisibleByViewport" />
    <v-list three-line>
      <template v-for="(transaction, index) in growing">
        <ac-transaction :key="transaction.id" :transaction="transaction" :username="user.username" :escrow="escrow" />
        <v-divider v-if="index + 1 < growing.length" :key="`divider-${index}`" />
      </template>
      <v-list-tile v-if="growing !== null && growing.length === 0">
        <v-list-tile-content>
          <v-list-tile-title>No matching transactions exist.</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
    </v-list>
    <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" :total-visible="totalVisibleByViewport" />
  </v-card>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import AcTransaction from './ac-transaction'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import { EventBus } from '../lib'

  export default {
    components: {AcTransaction},
    mixins: [Viewer, Perms, Paginated],
    props: ['endpoint', 'escrow'],
    data () {
      return {
        url: this.endpoint
      }
    },
    methods: {
      resetTransactions () {
        this.response = null
        this.growing = null
        this.fetchItems()
      }
    },
    created () {
      EventBus.$on('updated-transactions', this.resetTransactions)
    },
    destroyed () {
      EventBus.$off('updated-transactions', this.resetTransactions)
    }
  }
</script>
