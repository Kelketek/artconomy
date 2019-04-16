<template>
  <v-layout row wrap>
    <v-flex xs12 sm6 text-xs-center class="pa-2" d-flex>
      <v-layout row justify-content align-center>
        <v-flex>
          <ac-load-section :controller="balance" v-if="!nonUsAccount">
            <template v-slot:default>
              <v-card>
                <v-card-text>
                  <p><strong>Escrow Balance: ${{balance.x.escrow}}</strong></p>
                  <p><strong>Available Balance: ${{balance.x.available}}</strong></p>
                  <p><strong>In transit to your bank: ${{balance.x.pending}}</strong></p>
                </v-card-text>
              </v-card>
            </template>
          </ac-load-section>
          <ac-load-section :controller="subjectHandler.artistProfile">
            <template v-slot:default>
              <v-flex py-1>
                <ac-patch-field field-type="ac-bank-toggle"
                                :patcher="subjectHandler.artistProfile.patchers.bank_account_status"
                                :username="username" :manage-banks="true"
                ></ac-patch-field>
              </v-flex>
            </template>
          </ac-load-section>
        </v-flex>
      </v-layout>
    </v-flex>
    <v-flex xs12 sm6 text-xs-center class="pa-2">
      <v-layout row wrap>
        <v-flex xs8 offset-xs2 sm6 offset-sm3 md4 offset-md4>
          <v-img src="/static/images/defending.png" contain class="shield-indicator" :class="{faded: nonUsAccount}"></v-img>
        </v-flex>
        <v-flex xs12 text-xs-center>
          <p v-if="nonUsAccount">Artconomy Shield is disabled.</p>
          <p v-else>Artconomy Shield is enabled!</p>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<style scoped>
  .shield-indicator {
    transition: opacity 1s;
  }
  .faded {
    opacity: .25;
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcBankToggle from '@/components/fields/AcBankToggle.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {SingleController} from '@/store/singles/controller'
import {Balance} from '@/types/Balance'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {ListController} from '@/store/lists/controller'
import {Bank} from '@/types/Bank'
  @Component({
    components: {AcFormDialog, AcPatchField, AcLoadSection, AcBankToggle},
  })
export default class Payout extends mixins(Subjective) {
    public privateView = true
    public balance: SingleController<Balance> = null as unknown as SingleController<Balance>
    public banks: ListController<Bank> = null as unknown as ListController<Bank>
    // Can't use the enum in import or it will choke during testing. :/
    public NO_US_ACCOUNT = 2
    public get nonUsAccount() {
      // Should be synced this way.
      const profile = this.subjectHandler.artistProfile
      return profile.x && (profile.patchers.bank_account_status.model === this.NO_US_ACCOUNT)
    }
    public created() {
      this.subjectHandler.artistProfile.get().catch(this.setError)
      this.banks = this.$getList(
        `${this.username}__banks`, {endpoint: `/api/sales/v1/account/${this.username}/banks/`, paginated: false}
      )
      this.banks.firstRun()
      this.balance = this.$getSingle(
        `${this.username}__balance`, {endpoint: `/api/sales/v1/account/${this.username}/balance/`}
      )
      this.balance.get()
    }
}
</script>
