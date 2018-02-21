<template>
  <div v-if="response">
    <p><strong>Escrow Balance: ${{response.escrow}}</strong></p>
    <p><strong>Available Balance: ${{response.available}}</strong></p>
  </div>
</template>

<script>
  import { artCall } from '../lib'
  import Perms from '../mixins/permissions'

  export default {
    name: 'ac-account-balance',
    mixins: [Perms],
    data () {
      return {
        response: null
      }
    },
    methods: {
      populateBalance (response) {
        this.response = response
      },
      populateBanks (response) {
        this.accounts = response
      }
    },
    created () {
      artCall(`/api/sales/v1/account/${this.username}/balance/`, 'GET', undefined, this.populateBalance)
      artCall(`/api/sales/v1/account/${this.username}/accounts/`, 'GET', undefined, this.populateBanks)
    }
  }
</script>