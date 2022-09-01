<template>
  <v-row no-gutters  >
    <v-col cols="12" sm="8" md="6" class="pa-2 text-center d-flex" >
      <v-row no-gutters class="justify-content"  align="center">
        <v-col>
          <ac-load-section :controller="balance" v-if="inSupportedCountry">
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
              <v-col class="py-1" >
                <ac-patch-field field-type="ac-bank-toggle"
                                :patcher="subjectHandler.artistProfile.patchers.bank_account_status"
                                :username="username" :manage-banks="true"
                ></ac-patch-field>
              </v-col>
            </template>
          </ac-load-section>
        </v-col>
      </v-row>
    </v-col>
    <v-col cols="12" sm="4" md="6" class="pa-2 text-center">
      <v-row no-gutters  >
        <v-col cols="8" offset="2" sm="6" offset-sm="3" md="4" offset-md="4">
          <v-img src="/static/images/defending.png" contain class="shield-indicator" :class="{faded: !inSupportedCountry}"></v-img>
        </v-col>
        <v-col class="text-center" cols="12" >
          <p v-if="inSupportedCountry">Artconomy Shield is enabled!</p>
          <p v-else>Artconomy Shield is disabled.</p>
        </v-col>
      </v-row>
    </v-col>
    <v-col v-if="hasActiveStripe">
      <v-card>
        <v-card-text>
          <v-row>
            <v-col cols="12" v-if="defaultProcessor === AUTHORIZE">
              <h2>Your bank account is configured, and you are set up with Stripe!</h2>
              <p>Your products will be protected by <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link>.</p>
              <p>Eventually, all artists will be moved over to this processor. You are ahead of the game!</p>
            </v-col>
            <v-col cols="12" v-else>
              <h2>Your bank account is configured, and you can now list products!</h2>
              <p>Your products will be protected by <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link>.</p>
              <p>If you need to update your bank settings, visit your <a target="_blank" rel="noopener" href="https://dashboard.stripe.com/">Stripe Dashboard.</a></p>
            </v-col>
            <v-col cols="12">
              <v-btn color="primary" :to="{name: 'Store', params: {username}}">Go to my Store</v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col v-if="banks.list.length">
      <v-row no-gutters>
        <v-col v-if="defaultProcessor === STRIPE && !stripeAccounts.list.length">
          <h2>You are currently using the legacy payout system.</h2>
          <p>Please remove this bank from your account and complete Stripe setup.</p>
        </v-col>
        <v-col cols="12" v-for="bank in banks.list" :key="bank.x.id">
          <v-card>
            <v-card-text>
              <v-row no-gutters class="justify-content" align="center">
                <v-col class="bank-label text-left" align-self="center">
                  <span v-if="bank.x.type === 0">Checking</span>
                  <span v-else>Savings</span>
                  ending in {{bank.x.last_four}}
                </v-col>
                <v-col class="shrink" >
                  <ac-confirmation :action="() => bank.delete().then(subjectHandler.user.refresh)">
                    <template v-slot:default="confirmContext">
                      <v-btn icon color="danger" v-on="confirmContext.on">
                        <v-icon>delete</v-icon>
                      </v-btn>
                    </template>
                  </ac-confirmation>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-col>
  </v-row>
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
import {flatten} from '@/lib/lib'
import StripeAccount from '@/types/StripeAccount'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import {User} from '@/store/profiles/types/User'
import {PROCESSORS} from '@/types/PROCESSORS'
import {BANK_STATUSES} from '@/store/profiles/types/BANK_STATUSES'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'

  @Component({
    components: {AcConfirmation, AcBoundField, AcFormContainer, AcFormDialog, AcPatchField, AcLoadSection, AcBankToggle},
  })
export default class Payout extends mixins(Subjective) {
    public privateView = true
    public balance: SingleController<Balance> = null as unknown as SingleController<Balance>
    public banks: ListController<Bank> = null as unknown as ListController<Bank>
    public stripeAccounts: ListController<StripeAccount> = null as unknown as ListController<StripeAccount>
    // Can't use the enum in import or it will choke during testing. :/
    public IN_SUPPORTED_COUNTRY = BANK_STATUSES.IN_SUPPORTED_COUNTRY

    public defaultProcessor = window.DEFAULT_CARD_PROCESSOR

    public AUTHORIZE = PROCESSORS.AUTHORIZE
    public STRIPE = PROCESSORS.STRIPE

    public get inSupportedCountry() {
      // Should be synced this way.
      const profile = this.subjectHandler.artistProfile
      /* istanbul ignore next */
      return profile.x && (profile.patchers.bank_account_status.model === this.IN_SUPPORTED_COUNTRY)
    }

    public get hasActiveStripe() {
      return this.stripeAccounts.list.filter((controller) => controller.x!.active).length
    }

    public created() {
      // @ts-ignore
      window.payout = this
      this.subjectHandler.artistProfile.get().catch(this.setError)
      this.banks = this.$getList(
        `${flatten(this.username)}__banks`, {endpoint: `/api/sales/v1/account/${this.username}/banks/`, paginated: false},
      )
      const viewer = this.viewer as User
      this.stripeAccounts = this.$getList(
        `${flatten(this.username)}__stripeAccounts`, {
          endpoint: `/api/sales/v1/account/${this.username}/stripe-accounts/`,
          paginated: false,
          socketSettings: {
            appLabel: 'sales',
            modelName: 'StripeAccount',
            serializer: 'StripeAccountSerializer',
            list: {
              appLabel: 'profiles',
              modelName: 'User',
              pk: `${viewer.id}`,
              listName: 'stripe_accounts',
            },
          },
        },
      )
      this.stripeAccounts.firstRun()
      this.banks.firstRun()
      this.balance = this.$getSingle(
        `${flatten(this.username)}__balance`, {endpoint: `/api/sales/v1/account/${this.username}/balance/`},
      )
      this.balance.get()
    }
}
</script>
