<template>
  <v-layout row wrapped text-xs-center>
    <v-flex xs12>
      <v-card v-if="growing && growing.length">
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" />
        <v-list three-line>
          <template v-for="(transaction, index) in growing">
            <ac-transaction :key="transaction.id" :transaction="transaction" :username="user.username" />
            <v-divider v-if="index + 1 < growing.length" :key="`divider-${index}`" />
          </template>
        </v-list>
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" />
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import AcTransaction from './ac-transaction'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import {EventBus} from '../lib'

  export default {
    components: {AcTransaction},
    mixins: [Viewer, Perms, Paginated],
    props: ['endpoint'],
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
      this.fetchItems()
    },
    destroyed () {
      EventBus.$off('updated-transactions', this.resetTransactions)
    }
  }
</script>