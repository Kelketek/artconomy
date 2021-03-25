<template>
  <v-col v-if="!manageBanks || banks.empty">
    <v-row v-if="value === UNSET">
      <v-col cols="12">
        <h2>Do you have a US Bank account?</h2>
      </v-col>
      <v-col cols="12" sm="6">
        <v-btn color="primary" @click="input(IN_SUPPORTED_COUNTRY)" class="have-us-account">Yes, I have a US Bank account</v-btn>
      </v-col>
      <v-col cols="12" sm="6">
        <v-btn color="danger" @click="input(NO_SUPPORTED_COUNTRY)" class="no-us-account">No, I do not have a US Bank account</v-btn>
      </v-col>
      <v-col cols="12">
        <p><strong>Note:</strong> You may still list products and take orders on Artconomy if you do not have a
          US Bank account. But you will not be able to use <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link> to protect your sales.</p>
      </v-col>
    </v-row>
    <v-row v-else-if="value === IN_SUPPORTED_COUNTRY">
      <v-col cols="12">
        <h2>You can now list products!</h2>
        <p>Your products will be protected by <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link>!</p>
      </v-col>
      <v-col cols="12" sm="6">
        <v-btn color="primary" v-if="manageBanks && banks.empty" @click="showAddBank = true" class="add-account" :disabled="!canAddBank">Add bank account</v-btn>
      </v-col>
      <v-col cols="12" sm="6">
        <v-btn color="danger" @click="input(NO_SUPPORTED_COUNTRY)" class="no-us-account">I don't have a US Bank account</v-btn>
      </v-col>
      <v-col cols="12" v-if="manageBanks && banks.empty && !canAddBank">
        <v-alert type="info">You may not add a bank account until you have earned at least $1. This is to cover the one-time connection fee required by our payment processor.</v-alert>
      </v-col>
    </v-row>
    <v-col v-else-if="value === NO_SUPPORTED_COUNTRY">
      <h2>You may now list products!</h2>
      <p>Your products will not be protected by Artconomy Shield, but you will still be able to list products, take orders, and use other features of the site.</p>
      <v-btn color="primary" @click="input(IN_SUPPORTED_COUNTRY)" class="have-us-account">I have a US bank account</v-btn>
    </v-col>
    <ac-form-dialog
        v-if="manageBanks"
        v-model="showAddBank"
        v-bind="newBank.bind"
        @submit.prevent="newBank.submitThen(addBank)"
        title="Add Bank"
    >
      <template v-slot:header v-if="willIncurFee.x && willIncurFee.x.value">
        <v-row>
          <v-col class="text-center">
            <p><strong>Note: There will be a one-time connection fee of $1 assessed, as required by our payment processor.</strong></p>
          </v-col>
        </v-row>
      </template>
      <v-row no-gutters>
        <v-col cols="12" sm="6">
          <ac-bound-field :field="newBank.fields.first_name" label="First Name" hint="The first name of the person primarily responsible for the account."></ac-bound-field>
        </v-col>
        <v-col cols="12" sm="6">
          <ac-bound-field :field="newBank.fields.last_name" label="Last Name" hint="The last name of the person primarily responsible for the account."></ac-bound-field>
        </v-col>
        <v-col cols="12" class="py-1">
          <v-img src="/static/images/check.svg" contain min-width="100%" :aspect-ratio="2.75" class="elevation-2"></v-img>
        </v-col>
        <v-col cols="12" sm="6">
          <ac-bound-field :field="newBank.fields.type" label="Account Type" :persistent-hint="true"
                          field-type="v-select"
                          :items="[{text: 'Checking', value: 0}, {text: 'Savings', value: 1}]"
                          hint="Please select whether your account is a checking or savings account."
          ></ac-bound-field>
        </v-col>
        <v-col cols="12" sm="6">
          <ac-bound-field :field="newBank.fields.routing_number" label="Routing Number"
                          hint="Check the diagram above to find your routing number on a check, or you can look at your most recent bank statement. If there is more than one routing number on your statement, select the one for Direct Deposit or ACH, not wire transfers."></ac-bound-field>
        </v-col>
        <v-col cols="12" sm="6">
          <ac-bound-field :field="newBank.fields.account_number" label="Account Number"
                          hint="Check the diagram above to find your account number on a check, or you can look at your most recent bank statement."></ac-bound-field>
        </v-col>
        <v-col cols="12" sm="6">
          <ac-bound-field :field="newBank.fields.account_number_confirmation" label="Confirm Account Number" hint="It's really important that the account number is correct. Your money won't end up in the right place if it's not!"></ac-bound-field>
        </v-col>
      </v-row>
    </ac-form-dialog>
  </v-col>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import {BANK_STATUSES} from '@/store/profiles/types/BANK_STATUSES'
import {ListController} from '@/store/lists/controller'
import {Bank} from '@/types/Bank'
import {FormController} from '@/store/forms/form-controller'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {flatten, genId} from '@/lib/lib'
import Subjective from '@/mixins/subjective'
import AcBoundField from '@/components/fields/AcBoundField'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {SingleController} from '@/store/singles/controller'
import {Balance} from '@/types/Balance'
import {PROCESSORS} from '@/types/PROCESSORS'

// Will probably never use this again, but can factor it out if I do.
declare type RemoteFlag = {
  value: boolean
}

  @Component({
    components: {AcConfirmation, AcBoundField, AcFormDialog},
  })
export default class AcBankToggleAuthorize extends mixins(Subjective) {
    @Prop({required: true})
    public value!: BANK_STATUSES

    @Prop({default: false})
    public manageBanks!: boolean

    public balance: SingleController<Balance> = null as unknown as SingleController<Balance>
    public banks: ListController<Bank> = null as unknown as ListController<Bank>
    public willIncurFee: SingleController<RemoteFlag> = null as unknown as SingleController<RemoteFlag>
    public showAddBank = false
    public newBank: FormController = null as unknown as FormController
    public UNSET = BANK_STATUSES.UNSET
    public IN_SUPPORTED_COUNTRY = BANK_STATUSES.IN_SUPPORTED_COUNTRY
    public NO_SUPPORTED_COUNTRY = BANK_STATUSES.NO_SUPPORTED_COUNTRY
    public AUTHORIZE = PROCESSORS.AUTHORIZE

    public input(val: BANK_STATUSES) {
      this.$emit('input', val)
    }

    public get bankUrl() {
      return `/api/sales/v1/account/${this.username}/banks/`
    }

    public addBank(response: Bank) {
      this.banks.push(response)
      this.showAddBank = false
    }

    public get canAddBank() {
      if (!this.willIncurFee.x) {
        return false
      }
      if (!this.willIncurFee.x.value) {
        return true
      }
      return this.balance.x && (parseFloat(this.balance.x.available) >= 1)
    }

    public created() {
      this.banks = this.$getList(
        `${flatten(this.username)}__banks`, {endpoint: this.bankUrl, paginated: false},
      )
      this.banks.firstRun()
      this.balance = this.$getSingle(
        `${flatten(this.username)}__balance`, {endpoint: `/api/sales/v1/account/${this.username}/balance/`},
      )
      this.balance.get()
      this.willIncurFee = this.$getSingle(
          `${flatten(this.username)}__bankFeeCheck`,
          {endpoint: `/api/sales/v1/account/${this.username}/banks/fee-check/`},
      )
      this.willIncurFee.get()
      this.newBank = this.$getForm(genId(), {
        fields: {
          type: {value: null},
          first_name: {value: '', validators: [{name: 'required'}]},
          last_name: {value: '', validators: [{name: 'required'}]},
          account_number: {
            value: '',
            validators: [
              {name: 'numeric'}, {name: 'required'}, {name: 'minLength', args: [4]},
              {name: 'maxLength', args: [17]},
            ],
          },
          account_number_confirmation: {
            value: '',
            validators: [
              {name: 'matches', args: ['account_number', 'Account numbers do not match!']},
            ],
          },
          routing_number: {
            value: '',
            validators: [
              {name: 'numeric'}, {name: 'required'}, {name: 'minLength', args: [9]},
              {name: 'maxLength', args: [9]},
            ],
          },
        },
        endpoint: this.bankUrl,
      })
    }
}
</script>
