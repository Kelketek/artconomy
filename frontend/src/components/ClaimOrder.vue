<template>
  <v-container grid-list-md>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center>
        <v-card>
          <v-card-text>
            <div v-if="loading">
              <h2>Finding your order...</h2>
              <v-progress-circular
                  indeterminate
                  color="purple" class="my-4"
              ></v-progress-circular>
            </div>
            <div v-else-if="statusCode === 404">
              <h2>This order does not exist, or has already been claimed by another account.</h2>
              <v-btn color="primary" :to="{name: 'Home'}" class="my-2">Ok.</v-btn>
            </div>
            <div v-else-if="statusCode === 403">
              <h2>Ready to Claim your Order?</h2>
              <v-btn color="primary" class="my-2"
                     :to="{name: 'Login', params: {tabName: 'register'}, query: {claim: claimToken, next: `/claim/order/${orderId}/${claimToken}/`}}"
              >Log in or Register to begin</v-btn>
            </div>
            <div v-else>
              <h2>There was an error claiming your order.</h2>
              <v-btn color="primary" class="my-2" @click="fetchOrder">Retry</v-btn><br />
              Or<br />
              <v-btn color="secondary" class="my-2" @click="showSupport">Contact Support</v-btn><br />
            </div>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import {artCall, EventBus} from '../lib'

  export default {
    name: 'ClaimOrder',
    props: ['claimToken', 'orderId'],
    data () {
      return {
        loading: true,
        baseUrl: `/api/sales/v1/claim/order/${this.orderId}/${this.claimToken}/`,
        statusCode: null
      }
    },
    methods: {
      fetchOrder () {
        this.loading = true
        this.statusCode = null
        artCall(this.baseUrl, 'POST', undefined, this.success, this.errorHandler)
      },
      showSupport () {
        EventBus.$emit('showSupport')
      },
      errorHandler(response) {
        this.loading = false
        this.statusCode = response.status
      },
      success (response) {
        this.$router.push({name: 'Order', params: {'username': this.viewer.username, 'orderID': response.id}})
      }
    },
    created () {
      this.fetchOrder()
    }
  }
</script>