<template>
  <v-layout row wrap v-if="response" text-xs-center class="mt-2">
    <v-flex xs12>
      <p><strong>Escrow Balance: ${{response.escrow}}</strong></p>
      <p><strong>Available Balance: ${{response.available}}</strong></p>
      <p>
        If auto-withdraw is enabled, available balance may always be 0, as transfers are started automatically.
        Please check your
        <router-link :to="{name: 'Settings', params: {tabName: 'payment', subTabName: 'transactions', tertiaryTabName: 'available'}}">
          transaction history</router-link> for more details.
      </p>
    </v-flex>
    <v-flex xs12 v-if="parseFloat(response.available) && accounts !== null && accounts.length !== 0">
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
            <v-flex v-if="!user.bank_account_status">
              <h3 class="display-3">Configure your payment settings!</h3>
              <span class="subheading">Do you have a US Bank account?</span>
              <v-divider class="my-3" />
              <ac-action large
                              :url="`/api/profiles/v1/account/${this.user.username}/settings/`"
                              method="PATCH" class="mx-0"
                              :success="updateUser"
                              color="primary"
                              :send="{bank_account_status: 1}"
              >I have a US Bank account</ac-action> <br />
              <ac-action large
                         :url="`/api/profiles/v1/account/${this.user.username}/settings/`"
                         method="PATCH" class="mx-0"
                         :success="updateUser"
                         color="red"
                         :send="{bank_account_status: 2}"
              >I do not have a US Bank account</ac-action>
            </v-flex>
            <v-flex v-else-if="user.bank_account_status === 1">
              <h3 class="display-3">You may now list products!</h3>
              <span class="subheading"><router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
                  Artconomy Shield</router-link> is enabled. You may add a bank account to collect your earnings below, or <router-link :to="{name: 'Store', username: user.username}">click here to start adding products!</router-link>.</span>
              <v-divider class="my-3" />
              <v-btn @click="showNewBank = true" color="primary">Add a US Bank Account</v-btn>
            </v-flex>
            <v-flex v-else>
              <h3 class="display-3">You may now list products!</h3>
              <span class="subheading">
                <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
                  Artconomy Shield</router-link> is disabled, <router-link :to="{name: 'Store', username: user.username}">
                but you may list products and sell them here!</router-link> If you obtain a US Banking account, you may
                enable shielding by pressing the button below.
              </span>
              <v-divider class="my-3" />
              <ac-action large
                         :url="`/api/profiles/v1/account/${this.user.username}/settings/`"
                         method="PATCH" class="mx-0"
                         :success="updateUser"
                         color="red"
                         :send="{bank_account_status: 1}"
              >I have a US Bank Account</ac-action>
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
        <p>Consent for bank transfers may be revoked by removing the bank information from your account.</p>
        <p>
          <strong>A $3 non-refundable connection fee is assessed upon connecting an account, as required by our payment
            processor. This will be deducted from your current balance. If your balance is not yet sufficient to cover
            this fee, you will not be able to add a bank at this time.
          </strong>
        </p>
      </v-flex>
    </ac-form-dialog>
    <v-flex xs12 v-if="user.bank_account_status && !(user.bank_account_status === 2) && (accounts !== null && accounts.length === 0)">
      <v-card class="mt-3">
        <v-card-text>
          <p>
            <span class="subheading">If you don't have a US Bank account, you can still list products on Artconomy and
                    take orders, but you will need to disable
                    <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
                      Artconomy Shield.</router-link>
            </span>
          </p>
          <ac-action large
                     :url="`/api/profiles/v1/account/${this.user.username}/settings/`"
                     method="PATCH" class="mx-0"
                     :success="updateUser"
                     color="red"
                     :send="{bank_account_status: 2}"
          >I do not have a US Bank account</ac-action>
          <v-divider class="my-3" v-if="user.escrow_disabled" />
          <span class="subheading" v-if="user.escrow_disabled">You may now <router-link :to="{name: 'Store', params: {username: user.username}}">set up products.</router-link></span>
        </v-card-text>
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script>
  import { artCall, accountTypes, ACCOUNT_TYPES, validNumber, EventBus } from '../lib'
  import Perms from '../mixins/permissions'
  import AcFormDialog from './ac-form-dialog'
  import VueFormGenerator from 'vue-form-generator'
  import AcAction from './ac-action'
  import AcPatchbutton from './ac-patchbutton'

  export default {
    components: {
      AcPatchbutton,
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
      updateUser () {
        // The arguments pushed to the success function evaluate as true, so we have to make sure none are passed.
        this.$root.$loadUser()
      },
      postWithdraw () {
        this.fetchBalance()
        this.showWithdraw = false
        EventBus.$emit('updated-transactions')
      },
      addBank (response) {
        this.showNewBank = false
        this.accounts.push(response)
        this.$root.$loadUser()
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