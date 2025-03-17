<template>
  <v-row no-gutters>
    <v-col cols="12" sm="8" md="6" class="pa-2 text-center d-flex">
      <v-row no-gutters class="justify-content" align="center">
        <v-col>
          <ac-load-section v-if="inSupportedCountry" :controller="balance">
            <template #default>
              <v-card>
                <v-card-text>
                  <p>
                    <strong>Escrow Balance: ${{ balance.x!.escrow }}</strong>
                  </p>
                  <p>
                    <strong
                      >Available Balance: ${{ balance.x!.available }}</strong
                    >
                  </p>
                  <p>
                    To see any active transfers, please check your Stripe
                    Dashboard using the button below.
                  </p>
                </v-card-text>
              </v-card>
            </template>
          </ac-load-section>
          <ac-load-section :controller="subjectHandler.artistProfile">
            <template #default>
              <v-col class="py-1">
                <ac-patch-field
                  field-type="ac-bank-toggle"
                  :patcher="
                    subjectHandler.artistProfile.patchers.bank_account_status
                  "
                  :username="username"
                  :manage-banks="true"
                />
              </v-col>
            </template>
          </ac-load-section>
        </v-col>
      </v-row>
    </v-col>
    <v-col cols="12" sm="4" md="6" class="pa-2 text-center">
      <v-row no-gutters>
        <v-col cols="8" offset="2" sm="6" offset-sm="3" md="4" offset-md="4">
          <v-img
            :src="defending.href"
            contain
            class="shield-indicator"
            :class="{ faded: !inSupportedCountry }"
            alt=""
            aria-hidden="true"
          />
        </v-col>
        <v-col class="text-center" cols="12">
          <p v-if="inSupportedCountry">Artconomy Shield is enabled!</p>
          <p v-else>Artconomy Shield is disabled.</p>
        </v-col>
      </v-row>
    </v-col>
    <v-col v-if="hasActiveStripe">
      <v-card>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <h2>
                Your bank account is configured, and you can now list products!
              </h2>
              <p>
                Your products can be protected by
                <router-link
                  :to="{ name: 'BuyAndSell', params: { question: 'shield' } }"
                >
                  Artconomy Shield
                </router-link>
                .
              </p>
            </v-col>
            <v-col cols="12" sm="6">
              <v-btn
                color="primary"
                :to="{ name: 'Store', params: { username } }"
                variant="flat"
              >
                Go to my Store
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6">
              <ac-form
                @submit.prevent="dashboardLinkForm.submitThen(goToDashboard)"
              >
                <ac-form-container v-bind="dashboardLinkForm.bind">
                  <v-btn color="secondary" variant="flat" type="submit">
                    Stripe Dashboard
                  </v-btn>
                </ac-form-container>
              </ac-form>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { useSubject } from "@/mixins/subjective.ts"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import { BASE_URL, flatten } from "@/lib/lib.ts"
import { useErrorHandling } from "@/mixins/ErrorHandling.ts"
import { useViewer } from "@/mixins/viewer.ts"
import { useList } from "@/store/lists/hooks.ts"
import { useSingle } from "@/store/singles/hooks.ts"
import { computed, Ref } from "vue"
import AcFormContainer from "@/components/wrappers/AcFormContainer.vue"
import { useForm } from "@/store/forms/hooks.ts"
import AcForm from "@/components/wrappers/AcForm.vue"
import type { Balance, StripeAccount, SubjectiveProps } from "@/types/main"
import { BankStatus } from "@/store/profiles/types/enums.ts"
import type { StaffPower, User } from "@/store/profiles/types/main"

const props = defineProps<SubjectiveProps>()

const { viewer, powers } = useViewer()
const userViewer = viewer as Ref<User>
const { subjectHandler } = useSubject({
  props,
  privateView: true,
  controlPowers: ["view_financials"] as StaffPower[],
})

const { setError } = useErrorHandling()

subjectHandler.artistProfile.get().catch(setError)

const stripeAccounts = useList<StripeAccount>(
  `${flatten(props.username)}__stripeAccounts`,
  {
    endpoint: `/api/sales/account/${props.username}/stripe-accounts/`,
    paginated: false,
    socketSettings: {
      appLabel: "sales",
      modelName: "StripeAccount",
      serializer: "StripeAccountSerializer",
      list: {
        appLabel: "profiles",
        modelName: "User",
        pk: `${userViewer.value.id}`,
        listName: "stripe_accounts",
      },
    },
  },
)
stripeAccounts.firstRun()
const balance = useSingle<Balance>(`${flatten(props.username)}__balance`, {
  endpoint: `/api/sales/account/${props.username}/balance/`,
})
balance.get()

const defending = new URL("/static/images/defending.png", BASE_URL)

const inSupportedCountry = computed(() => {
  // Should be synced this way.
  const profile = subjectHandler.artistProfile
  /* istanbul ignore next */
  return (
    profile.x &&
    profile.patchers.bank_account_status.model ===
      BankStatus.IN_SUPPORTED_COUNTRY
  )
})

const hasActiveStripe = computed(() => {
  return stripeAccounts.list.filter((controller) => controller.x!.active).length
})

const dashboardLinkForm = useForm(
  `${flatten(props.username)}__stripeDashboardLink`,
  {
    endpoint: `/api/sales/account/${props.username}/stripe-accounts/dashboard-link/`,
    fields: {},
  },
)

declare interface DashboardLinkData {
  admin_url: string
  dashboard_url: string
}

const newTab = (url: string) => {
  Object.assign(document.createElement("a"), {
    target: "_blank",
    rel: "noopener noreferrer",
    href: url,
  }).click()
}

const goToDashboard = (dashboardLinkData: DashboardLinkData) => {
  console.log(dashboardLinkData)
  if (powers.value.view_financials) {
    newTab(dashboardLinkData.admin_url)
  } else {
    newTab(dashboardLinkData.dashboard_url)
  }
}
</script>

<style scoped>
.shield-indicator {
  transition: opacity 1s;
}

.faded {
  opacity: 0.25;
}
</style>
