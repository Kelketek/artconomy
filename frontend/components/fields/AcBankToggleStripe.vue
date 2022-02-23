<template>
  <ac-load-section :controller="stripeAccounts">
    <template v-slot:default>
      <v-container v-if="value === UNSET || value === IN_SUPPORTED_COUNTRY" class="pa-0">
        <v-card v-if="(needStripe || restartStripe) && (!hasActiveStripe)">
          <v-card-text>
            <ac-form-container v-bind="stripeSetupForm.bind">
              <v-row>
                <v-col cols="12">
                  <ac-bound-field
                      :field="stripeSetupForm.fields.country" field-type="v-select" outlined
                      label="Select your country"
                      :items="stripeCountries.x.countries"
                  ></ac-bound-field>
                  <v-btn @click="stripeSetupForm.submit().then(redirect)" :disabled="!stripeSetupForm.fields.country.value" color="primary">Set up Account</v-btn>
                </v-col>
                <v-col cols="12">
                  <v-subheader>Can't find your country?</v-subheader>
                </v-col>
                <v-col cols="12">
                  <p>If your country isn't supported, or you wish to forgo shield protection altogether, click the button below. You'll still be able to list products, manage orders, and use other features of the site, but you'll have to handle payment on your own.</p>
                  <v-btn @click="() => $emit('input', NO_SUPPORTED_COUNTRY)" color="danger">Disable Shield</v-btn>
                </v-col>
              </v-row>
            </ac-form-container>
          </v-card-text>
        </v-card>
        <v-card v-else-if="!needStripe && !hasActiveStripe">
          <v-card-text>
            <ac-form-container v-bind="stripeSetupForm.bind">
              <v-row>
                <v-col cols="12">
                  <v-card-text>
                    You've started your account setup but it's not yet finished. Hit the button below to complete setup. Be sure to upload your ID/documents in the section that talks about 'needing verification.'
                  </v-card-text>
                </v-col>
                <v-col cols="6" class="text-center">
                  <v-btn @click="stripeSetupForm.submit().then(redirect)" :disabled="!stripeSetupForm.fields.country.value" color="primary">Finish Setup</v-btn>
                </v-col>
                <v-col cols="6" class="text-center">
                  <v-btn @click="() => restartStripe = true" color="danger">Start Over</v-btn>
                </v-col>
              </v-row>
            </ac-form-container>
          </v-card-text>
        </v-card>
      </v-container>
      <v-row v-else-if="manageBanks">
        <h2>You may now list products!</h2>
        <p>Your products will not be protected by Artconomy Shield, but you will still be able to list products, take orders, and use other features of the site.</p>
        <v-btn color="primary" @click="() => $emit('input', UNSET)" class="have-us-account">Re-enable Shield</v-btn>
      </v-row>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'
import {BANK_STATUSES} from '@/store/profiles/types/BANK_STATUSES'
import {ListController} from '@/store/lists/controller'
import {FormController} from '@/store/forms/form-controller'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {flatten} from '@/lib/lib'
import Subjective from '@/mixins/subjective'
import AcBoundField from '@/components/fields/AcBoundField'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {SingleController} from '@/store/singles/controller'
import {Balance} from '@/types/Balance'
import {User} from '@/store/profiles/types/User'
import StripeAccount from '@/types/StripeAccount'
import StripeCountryList from '@/types/StripeCountryList'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'

// Will probably never use this again, but can factor it out if I do.
declare type RemoteFlag = {
  value: boolean
}

  @Component({
    components: {AcFormContainer, AcLoadSection, AcConfirmation, AcBoundField, AcFormDialog},
  })
export default class AcBankToggleStripe extends mixins(Subjective) {
    @Prop({required: true})
    public value!: BANK_STATUSES

    @Prop({default: false})
    public manageBanks!: boolean

    public balance: SingleController<Balance> = null as unknown as SingleController<Balance>
    public stripeAccounts: ListController<StripeAccount> = null as unknown as ListController<StripeAccount>
    public willIncurFee: SingleController<RemoteFlag> = null as unknown as SingleController<RemoteFlag>
    public stripeCountries: SingleController<StripeCountryList> = null as unknown as SingleController<StripeCountryList>
    public stripeSetupForm: FormController = null as unknown as FormController
    public newBank: FormController = null as unknown as FormController
    public restartStripe = false
    public UNSET = BANK_STATUSES.UNSET
    public IN_SUPPORTED_COUNTRY = 1 as BANK_STATUSES.IN_SUPPORTED_COUNTRY
    public NO_SUPPORTED_COUNTRY = 2 as BANK_STATUSES.NO_SUPPORTED_COUNTRY

    public get hasActiveStripe() {
      return !!this.stripeAccounts.list.filter((controller) => controller.x!.active).length
    }

    public get needStripe() {
      return this.stripeAccounts.ready && this.stripeAccounts.list.length === 0
    }

    /* istanbul ignore next */
    public redirect({link}: {link: string}) {
      window.location.href = link
    }

    @Watch('stripeAccounts.list.length')
    public prePopulateCountry(length: number) {
      // When editing, we want the system to use the same country value so the backend won't destroy and recreate the
      // user's account, which would lose their progress. The backend destroys the account if we ask for a setup link
      // with a different country, since the user can't select that as part of Stripe's walkthrough setup.
      if (!length) {
        return
      }
      this.stripeSetupForm.fields.country.update(this.stripeAccounts.list[0].x!.country)
    }

    public created() {
      const subject = this.subject as User
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
              pk: `${subject.id}`,
              listName: 'stripe_accounts',
            },
          },
        },
      )
      this.stripeSetupForm = this.$getForm(
        `${flatten(this.username)}__stripeAccountLink`,
        {
          endpoint: `/api/sales/v1/account/${this.username}/stripe-accounts/link/`,
          fields: {
            country: {value: '', validators: [{name: 'required'}]},
            url: {value: window.location + ''},
          },
        },
      )
      this.stripeCountries = this.$getSingle('stripeCountries', {endpoint: '/api/sales/v1/stripe-countries/', persist: true, x: {countries: []}})
      this.stripeCountries.get()
      this.stripeAccounts.firstRun()
    }
}
</script>
