<template>
  <ac-load-section :controller="stripeAccounts">
    <template v-slot:default>
      <v-container v-if="modelValue === BankStatus.UNSET || modelValue === BankStatus.IN_SUPPORTED_COUNTRY" class="pa-0">
        <v-card v-if="(needStripe || restartStripe) && (!hasActiveStripe)">
          <v-card-text>
            <ac-form-container v-bind="stripeSetupForm.bind" v-if="stripeCountries.x">
              <v-row>
                <v-col cols="12">
                  <ac-bound-field
                      :field="stripeSetupForm.fields.country" field-type="v-select" outlined
                      label="Select your country"
                      :items="stripeCountries.x.countries"
                  ></ac-bound-field>
                  <v-btn @click="stripeSetupForm.submit().then(redirect)"
                         variant="flat"
                         :disabled="!stripeSetupForm.fields.country.value" color="primary">Set up Account
                  </v-btn>
                </v-col>
                <v-col cols="12">
                  <v-list-subheader>Can't find your country?</v-list-subheader>
                </v-col>
                <v-col cols="12">
                  <p>If your country isn't supported, or you wish to forgo shield protection altogether, click the
                    button below. You'll still be able to list products, manage orders, and use other features of the
                    site, but you'll have to handle payment on your own.</p>
                  <v-btn @click="() => $emit('update:modelValue', BankStatus.NO_SUPPORTED_COUNTRY)" color="danger" variant="flat">Disable Shield
                  </v-btn>
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
                    You've started your account setup but it's not yet finished. Hit the button below to complete setup.
                    Be sure to upload your ID/documents in the section that talks about 'needing verification.'
                  </v-card-text>
                </v-col>
                <v-col cols="6" class="text-center">
                  <v-btn @click="stripeSetupForm.submit().then(redirect)"
                         variant="flat"
                         :disabled="!stripeSetupForm.fields.country.value" color="primary">Finish Setup
                  </v-btn>
                </v-col>
                <v-col cols="6" class="text-center">
                  <v-btn @click="() => restartStripe = true" color="danger" variant="flat">Start Over</v-btn>
                </v-col>
              </v-row>
            </ac-form-container>
          </v-card-text>
        </v-card>
      </v-container>
      <v-row v-else-if="manageBanks">
        <h2>You may now list products!</h2>
        <p>Your products will not be protected by Artconomy Shield, but you will still be able to list products, take
          orders, and use other features of the site.</p>
        <v-btn color="primary" @click="() => $emit('update:modelValue', BankStatus.UNSET)" class="have-us-account" variant="flat">Re-enable
          Shield
        </v-btn>
      </v-row>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import {flatten} from '@/lib/lib.ts'
import {useSubject} from '@/mixins/subjective.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {computed, ref, watch} from 'vue'
import {useList} from '@/store/lists/hooks.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import {useForm} from '@/store/forms/hooks.ts'
import type {StripeAccount, StripeCountryList, SubjectiveProps} from '@/types/main'
import {BankStatus} from '@/store/profiles/types/enums.ts'
import {BankStatusValue} from '@/store/profiles/types/main'


const props = withDefaults(
    defineProps<{modelValue: BankStatusValue, manageBanks?: boolean} & SubjectiveProps>(),
    {
      manageBanks: false,
    },
)

const restartStripe = ref(false)

const {subject} = useSubject({ props })

const hasActiveStripe = computed(() => !!stripeAccounts.list.filter((controller) => controller.x!.active).length)

const needStripe = computed(() => stripeAccounts.ready && stripeAccounts.list.length === 0)

const stripeAccounts = useList<StripeAccount>(
    `${flatten(props.username)}__stripeAccounts`, {
      endpoint: `/api/sales/account/${props.username}/stripe-accounts/`,
      paginated: false,
      socketSettings: {
        appLabel: 'sales',
        modelName: 'StripeAccount',
        serializer: 'StripeAccountSerializer',
        list: {
          appLabel: 'profiles',
          modelName: 'User',
          pk: `${subject.value.id}`,
          listName: 'stripe_accounts',
        },
      },
    },
)
const stripeSetupForm = useForm(
    `${flatten(props.username)}__stripeAccountLink`,
    {
      endpoint: `/api/sales/account/${props.username}/stripe-accounts/link/`,
      fields: {
        country: {
          value: '',
          validators: [{name: 'required'}],
        },
        url: {value: window.location + ''},
      },
    },
)
const stripeCountries = useSingle<StripeCountryList>('stripeCountries', {
  endpoint: '/api/sales/stripe-countries/',
  persist: true,
  x: {countries: []},
})
stripeCountries.get()
stripeAccounts.firstRun()

/* istanbul ignore next */
const redirect = ({link}: { link: string }) => {
  window.location.href = link
}

watch(() => stripeAccounts.list.length, (length) => {
  // When editing, we want the system to use the same country value so the backend won't destroy and recreate the
  // user's account, which would lose their progress. The backend destroys the account if we ask for a setup link
  // with a different country, since the user can't select that as part of Stripe's walkthrough setup.
  if (!length) {
    return
  }
  stripeSetupForm.fields.country.update(stripeAccounts.list[0].x!.country)
})
</script>
