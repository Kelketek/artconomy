<template>
  <v-layout row wrap v-if="response" text-xs-center class="mt-2">
    <v-flex xs12>
      <p><strong>Escrow Balance: ${{response.escrow}}</strong></p>
      <p><strong>Available Balance: ${{response.available}}</strong></p>
    </v-flex>
    <v-flex xs12 v-if="response.available && accounts !== null && accounts.length !== 0">
      <v-btn color="primary" @click="showWithdraw = true">Withdraw Funds</v-btn>
      <ac-form-dialog ref="withdrawForm" :schema="withdrawSchema" :model="withdrawModel"
                      :options="bankOptions" :success="postWithdraw"
                      title="Withdraw Funds"
                      :url="`/api/sales/v1/account/${user.username}/withdraw/`"
                      v-model="showWithdraw"
      >
        <v-flex slot="header" text-xs-center>
          <strong>Available Balance: ${{response.available}}</strong>
        </v-flex>
      </ac-form-dialog>
    </v-flex>
    <v-flex xs12 v-if="accounts !== null && accounts.length">
      <v-list>
        <v-list-tile action v-for="account in accounts" :key="account.id">
          <v-list-tile-title>{{ACCOUNT_TYPES[account.type]}} ending in {{account.last_four}}</v-list-tile-title>
          <v-list-tile-action>
            <ac-action method="delete" :url="`/api/sales/v1/account/${user.username}/banks/${account.id}/`" :success="fetchBanks">
              <v-icon>delete</v-icon>
            </ac-action>
          </v-list-tile-action>
        </v-list-tile>
      </v-list>
    </v-flex>
    <v-flex xs12>
      <v-jumbotron v-if="accounts !== null && accounts.length === 0" color="grey darken-3">
        <v-container fill-height>
          <v-layout align-center>
            <v-flex>
              <h3 class="display-3">Add a bank account!</h3>
              <span class="subheading">Add your account information so that we can send you the money you earn through Artconomy.</span>
              <v-divider class="my-3" />
              <v-btn large color="primary" class="mx-0" @click="showNewBank = true">Get Started</v-btn>
            </v-flex>
          </v-layout>
        </v-container>
      </v-jumbotron>
    </v-flex>
    <ac-form-dialog ref="bankForm" :schema="bankSchema" :model="bankModel"
                    :options="bankOptions" :success="addBank"
                    title="Add Bank"
                    :url="`/api/sales/v1/account/${this.user.username}/banks/`"
                    v-model="showNewBank"
    >
      <v-flex slot="header" text-xs-center xs12>
        <p><strong>Only US Banks are supported at this time.</strong></p>
        <p>Bank Transfers are subject to agreement with the <a href="https://www.dwolla.com/legal/tos/">Dwolla Terms of Service.</a> Consent may be revoked by removing the bank information from your account.</p>
      </v-flex>
    </ac-form-dialog>
  </v-layout>
</template>

<script>
  import { artCall, accountTypes, ACCOUNT_TYPES, validNumber, EventBus } from '../lib'
  import Perms from '../mixins/permissions'
  import AcFormDialog from './ac-form-dialog'
  import VueFormGenerator from 'vue-form-generator'
  import AcAction from './ac-action'

  export default {
    components: {
      AcAction,
      AcFormDialog},
    name: 'ac-account-balance',
    mixins: [Perms],
    data () {
      return {
        response: null,
        accounts: null,
        showNewBank: false,
        showWithdraw: false,
        bankModel: {
          first_name: '',
          last_name: '',
          type: '0',
          account_number: '',
          routing_number: ''
        },
        bankSchema: {
          fields: [{
            type: 'v-text',
            label: 'First Name',
            model: 'first_name',
            featured: true,
            validator: VueFormGenerator.validators.required
          }, {
            type: 'v-text',
            label: 'Last Name',
            model: 'last_name',
            featured: true,
            validator: VueFormGenerator.validators.required
          }, {
            type: 'v-select',
            label: 'Account Type',
            model: 'type',
            values: accountTypes,
            selectOptions: {
              hideNoneSelectedText: true
            }
          }, {
            type: 'v-text',
            label: 'Account Number',
            model: 'account_number',
            mask: '#################################################',
            featured: true,
            validator: VueFormGenerator.validators.required
          }, {
            type: 'v-text',
            label: 'Routing Number',
            model: 'routing_number',
            mask: '#########',
            placeholder: '',
            featured: true,
            min: 9,
            max: 9,
            counter: 9,
            validator: [VueFormGenerator.validators.required, VueFormGenerator.validators.string]
          }]
        },
        bankOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        withdrawModel: {
          amount: 0,
          bank: null
        },
        withdrawSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'number',
            min: 1,
            max: 1,
            step: '.01',
            label: 'Amount (USD)',
            model: 'amount',
            validator: [VueFormGenerator.validators.required, validNumber]
          }, {
            type: 'v-select',
            values: [],
            model: 'bank',
            validator: [VueFormGenerator.validators.required]
          }]
        },
        ACCOUNT_TYPES: ACCOUNT_TYPES
      }
    },
    methods: {
      fetchBalance () {
        artCall(`/api/sales/v1/account/${this.username}/balance/`, 'GET', undefined, this.populateBalance)
      },
      fetchBanks () {
        artCall(`/api/sales/v1/account/${this.username}/banks/`, 'GET', undefined, this.populateBanks)
      },
      populateBalance (response) {
        this.response = response
        this.withdrawSchema.fields[0].max = response.available + ''
      },
      populateBanks (response) {
        this.accounts = response.results
        this.withdrawSchema.fields[1].values = this.bankValues
        if (this.accounts.length > 0) {
          this.withdrawModel.bank = this.accounts[0].id + ''
        }
      },
      postWithdraw () {
        this.fetchBalance()
        this.showWithdraw = false
        EventBus.$emit('updated-transactions')
      },
      addBank (response) {
        this.showNewBank = false
        this.accounts.push(response)
      }
    },
    computed: {
      bankValues () {
        let banks = []
        for (let bank of this.accounts) {
          banks.push({
            value: bank.id + '',
            text: `${ACCOUNT_TYPES[bank.type]} ending in ${bank.last_four}`
          })
        }
        return banks
      }
    },
    created () {
      this.fetchBalance()
      this.fetchBanks()
    }
  }
</script>