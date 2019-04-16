<template>
  <v-flex v-if="!manageBanks || banks.empty">
    <v-flex v-if="value === UNSET">
      <h2>Do you have a US Bank account?</h2>
      <v-btn color="primary" @click="input(HAS_US_ACCOUNT)" class="have-us-account">Yes, I have a US Bank account</v-btn>
      <v-btn color="danger" @click="input(NO_US_ACCOUNT)" class="no-us-account">No, I do not have a US Bank account</v-btn>
      <p><strong>Note:</strong> You may still list products and take orders on Artconomy if you do not have a
        US Bank account. But you will not be able to use <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link> to protect your sales.</p>
    </v-flex>
    <v-flex v-else-if="value === HAS_US_ACCOUNT">
      <h2>You can now list products!</h2>
      <p>Your products will be protected by <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link>!</p>
      <v-btn color="primary" v-if="manageBanks && banks.empty" @click="showAddBank = true" class="add-account">Add bank account</v-btn>
      <v-btn color="danger" @click="input(NO_US_ACCOUNT)" class="no-us-account">I don't have a US Bank account</v-btn>
    </v-flex>
    <v-flex v-else-if="value === NO_US_ACCOUNT">
      <h2>You may now list products!</h2>
      <p>Your products will not be protected by Artconomy Shield, but you will still be able to list products, take orders, and use other features of the site.</p>
      <v-btn color="primary" @click="input(HAS_US_ACCOUNT)" class="have-us-account">I have a US bank account</v-btn>
    </v-flex>
    <ac-form-dialog
        v-if="manageBanks"
        v-model="showAddBank"
        v-bind="newBank.bind"
        @submit.prevent="newBank.submitThen(addBank)"
        title="Add Bank"
    >
      <v-layout row wrap>
        <v-flex slot="header" text-xs-center>
          <p><strong>Note: There will be a one-time connection fee of $1 assessed, as required by our payment processor.</strong></p>
        </v-flex>
        <v-flex xs12 sm6>
          <ac-bound-field :field="newBank.fields.first_name" label="First Name" hint="The first name of the person primarily responsible for the account."></ac-bound-field>
        </v-flex>
        <v-flex xs12 sm6>
          <ac-bound-field :field="newBank.fields.last_name" label="Last Name" hint="The last name of the person primarily responsible for the account."></ac-bound-field>
        </v-flex>
        <v-flex xs12 class="py-1">
          <v-img src="/static/images/check.svg" contain min-width="100%" :aspect-ratio="2.75" class="elevation-2"></v-img>
        </v-flex>
        <v-flex xs12 sm6>
          <ac-bound-field :field="newBank.fields.type" label="Account Type" :persistent-hint="true"
                          field-type="v-select"
                          :items="[{text: 'Checking', value: 0}, {text: 'Savings', value: 1}]"
                          hint="Please select whether your account is a checking or savings account."
          ></ac-bound-field>
        </v-flex>
        <v-flex xs12 sm6>
          <ac-bound-field :field="newBank.fields.routing_number" label="Routing Number"
                          hint="Check the diagram above to find your routing number on a check, or you can look at your most recent bank statement. If there is more than one routing number on your statement, select the one for Direct Deposit or ACH, not wire transfers."></ac-bound-field>
        </v-flex>
        <v-flex xs12 sm6>
          <ac-bound-field :field="newBank.fields.account_number" label="Account Number"
                          hint="Check the diagram above to find your account number on a check, or you can look at your most recent bank statement."></ac-bound-field>
        </v-flex>
        <v-flex xs12 sm6>
          <ac-bound-field :field="newBank.fields.account_number_confirmation" label="Confirm Account Number" hint="It's really important that the account number is correct. Your money won't end up in the right place if it's not!"></ac-bound-field>
        </v-flex>
      </v-layout>
    </ac-form-dialog>
  </v-flex>
  <v-flex v-else>
    <v-layout row wrap>
      <v-flex xs12 v-for="bank in banks.list" :key="bank.x.id">
        <v-card>
          <v-card-text>
            <v-layout row justify-content align-center>
              <v-flex shrink class="bank-label">
                <span v-if="bank.x.type === 0">Checking</span>
                <span v-else>Savings</span>
                ending in {{bank.x.last_four}}
              </v-flex>
              <v-spacer />
              <v-flex shrink>
                <ac-confirmation :action="bank.delete">
                  <template v-slot:default="confirmContext">
                    <v-btn icon color="danger" v-on="confirmContext.on">
                      <v-icon>delete</v-icon>
                    </v-btn>
                  </template>
                </ac-confirmation>
              </v-flex>
            </v-layout>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
  </v-flex>
</template>

<script lang="ts">
import Vue from 'vue'
import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import {BankStatus} from '@/store/profiles/types/BankStatus'
import {ListController} from '@/store/lists/controller'
import {Bank} from '@/types/Bank'
import {FormController} from '@/store/forms/form-controller'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {genId} from '@/lib'
import Subjective from '@/mixins/subjective'
import AcBoundField from '@/components/fields/AcBoundField'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {SingleController} from '@/store/singles/controller'
  @Component({
    components: {AcConfirmation, AcBoundField, AcFormDialog},
  })
export default class AcBankToggle extends mixins(Subjective) {
    @Prop({required: true})
    public value!: BankStatus
    @Prop({default: false})
    public manageBanks!: boolean
    public banks: ListController<Bank> = null as unknown as ListController<Bank>
    public showAddBank = false
    public newBank: FormController = null as unknown as FormController
    public UNSET = 0 as BankStatus
    public HAS_US_ACCOUNT = 1 as BankStatus
    public NO_US_ACCOUNT = 2 as BankStatus

    public input(val: BankStatus) {
      this.$emit('input', val)
    }
    public get bankUrl() {
      return `/api/sales/v1/account/${this.username}/banks/`
    }
    public addBank(response: Bank) {
      this.banks.push(response)
      this.showAddBank = false
    }
    public created() {
      this.banks = this.$getList(
        `${this.username}__banks`, {endpoint: this.bankUrl, paginated: false}
      )
      this.banks.firstRun()
      this.newBank = this.$getForm(genId(), {fields: {
        type: {value: null},
        first_name: {value: '', validators: [{name: 'required'}]},
        last_name: {value: '', validators: [{name: 'required'}]},
        account_number: {value: '',
          validators: [
            {name: 'numeric'}, {name: 'required'}, {name: 'minLength', args: [4]},
            {name: 'maxLength', args: [17]},
          ]},
        account_number_confirmation: {value: '',
          validators: [
            {name: 'matches', args: ['account_number', 'Account numbers do not match!']},
          ]},
        routing_number: {value: '',
          validators: [
            {name: 'numeric'}, {name: 'required'}, {name: 'minLength', args: [9]},
            {name: 'maxLength', args: [9]},
          ]},
      },
      endpoint: this.bankUrl})
    }
}
</script>