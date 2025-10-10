<template>
  <v-container>
    <v-card color="grey-darken-3">
      <v-card-text>
        <v-row no-gutters>
          <v-col>
            <h1>Upgrade Your Account</h1>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <v-window v-model="tab">
      <v-window-item value="selection">
        <ac-load-section :controller="pricing">
          <template v-if="selection === null" #default>
            <v-row>
              <v-col cols="12" class="mt-5 mb-0">
                <v-alert type="info" class="ma-0">
                  Not sure which plan is best for you? Want to get a REAL
                  rundown of fees?
                  <router-link :to="{ name: 'Calculator' }"
                    >Check out our calculator!</router-link
                  >
                </v-alert>
              </v-col>
              <v-col
                v-for="(plan, index) in plans"
                :id="`plan-${flatten(plan.name)}-column`"
                :key="plan.id"
                cols="12"
                md="4"
                class="plan-column"
              >
                <v-card
                  style="height: 100%"
                  :color="current.colors['well-darken-2']"
                  class="d-flex flex-column"
                >
                  <v-card-text>
                    <v-row>
                      <v-col class="text-center" cols="12">
                        <v-card>
                          <v-card-title class="d-block text-center">
                            {{ plan.name }}
                          </v-card-title>
                          <v-card-text>{{ plan.description }}</v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>
                  </v-card-text>
                  <v-card-text
                    class="flex-fill align-self-baseline align-content-start"
                  >
                    <v-row class="fill-height" no-gutters>
                      <v-col cols="12">
                        <v-list two-line>
                          <v-list-item
                            v-if="
                              features[plan.id].length &&
                              plans.length > 1 &&
                              index !== 0
                            "
                          >
                            <strong>...All that, plus:</strong>
                          </v-list-item>
                          <template
                            v-for="(feature, innerIndex) in features[plan.id]"
                            :key="feature"
                          >
                            <v-list-item>
                              {{ feature }}
                            </v-list-item>
                            <v-divider
                              v-if="innerIndex !== features[plan.id].length - 1"
                              :key="`divider-${feature}`"
                            />
                          </template>
                        </v-list>
                      </v-col>
                    </v-row>
                  </v-card-text>
                  <v-card-actions
                    class="justify-center align-self-end text-center"
                    style="width: 100%"
                  >
                    <v-row>
                      <v-col cols="12">
                        <v-card>
                          <v-card-text class="text-center">
                            <div>
                              <span
                                v-if="!plan.max_simultaneous_orders"
                                class="text-h4"
                                >${{ plan.monthly_charge }} Monthly</span
                              >
                              <span v-else-if="!toFloat(plan.monthly_charge)">
                                <span class="text-h4">FREE</span>
                              </span>
                            </div>
                            <div>
                              Shield fee:
                              {{ plan.shield_percentage_price }}%<sup
                                v-if="
                                  pricing.x!.international_conversion_percentage
                                "
                                >*</sup
                              >
                              <span v-if="plan.shield_static_price"
                                >+ ${{ plan.shield_static_price }}</span
                              >
                            </div>
                            <div v-if="plan.per_deliverable_price">
                              Non-shield order tracking fee: ${{
                                plan.per_deliverable_price
                              }}
                            </div>
                            <div>
                              <div v-if="plan.max_simultaneous_orders">
                                Up to
                                {{ plan.max_simultaneous_orders }} order<span
                                  v-if="!(plan.max_simultaneous_orders === 1)"
                                  >s</span
                                >
                                at a time
                              </div>
                              <div v-else-if="!plan.per_deliverable_price">
                                Track Unlimited Orders
                              </div>
                            </div>
                            <div
                              v-if="
                                pricing.x!.international_conversion_percentage
                              "
                            >
                              <sup
                                >* Transfers outside the US include an
                                additional
                                {{
                                  pricing.x!
                                    .international_conversion_percentage
                                }}% conversion fee.</sup
                              ><br />
                              <sup>
                                Additional fees levied by stripe apply to all
                                shielded transactions. Please check the
                                <router-link :to="{ name: 'Calculator' }"
                                  >calculator</router-link
                                >
                                for details.
                              </sup>
                            </div>
                          </v-card-text>
                        </v-card>
                      </v-col>
                      <v-col cols="12">
                        <v-chip
                          v-if="
                            plan.name === loggedInViewer.next_service_plan &&
                            !toFloat(plan.monthly_charge)
                          "
                          color="gray"
                          class="current-plan-indicator"
                          variant="flat"
                          light
                        >
                          <strong>Your Current Plan</strong>
                        </v-chip>
                        <template v-else>
                          <v-btn
                            v-if="
                              !(plan.name === loggedInViewer.next_service_plan)
                            "
                            color="primary"
                            variant="flat"
                            class="select-plan-button"
                            @click="selection = plan.name"
                          >
                            Switch to {{ plan.name }}!
                          </v-btn>
                          <v-btn
                            v-else
                            :to="{
                              name: 'Premium',
                              params: { username: viewer!.username },
                            }"
                            class="manage-plan-button"
                            variant="flat"
                          >
                            Manage {{ plan.name }}
                          </v-btn>
                        </template>
                      </v-col>
                    </v-row>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>
          </template>
        </ac-load-section>
      </v-window-item>
      <v-window-item value="payment">
        <v-card v-if="selectedPlan && nonFree">
          <ac-form @submit.prevent="paymentSubmit">
            <ac-form-container v-bind="paymentForm.bind">
              <v-row v-if="selection" class="mt-3">
                <v-col cols="12">
                  <ac-card-manager
                    ref="cardManager"
                    v-model="paymentForm.fields.card_id.model"
                    :payment="true"
                    :username="viewer!.username"
                    :cc-form="paymentForm"
                    :field-mode="true"
                    :show-save="false"
                    :save-only="!toFloat(selectedPlan.monthly_charge)"
                    :client-secret="
                      (clientSecret.x && clientSecret.x.secret) || ''
                    "
                    @payment-sent="postPay"
                    @card-added="setPlan"
                  />
                </v-col>
                <v-col cols="12" class="pricing-container text-center">
                  <strong
                    >Monthly charge: ${{ selectedPlan.monthly_charge }}</strong
                  >
                  <br />
                  <div v-if="selectedPlan.per_deliverable_price">
                    Any orders tracked which aren't covered by shield protection
                    will be billed at ${{ selectedPlan.per_deliverable_price }}
                    at the end of your billing cycle.
                  </div>
                  <div class="mt-2 text-center">
                    <v-btn
                      class="mx-1"
                      variant="flat"
                      @click="selection = null"
                    >
                      Go back
                    </v-btn>
                    <v-btn
                      type="submit"
                      color="primary"
                      class="mx-1"
                      variant="flat"
                    >
                      Start Service
                    </v-btn>
                    <p>
                      Premium services, as with all use of Artconomy's
                      offerings, are subject to the
                      <router-link :to="{ name: 'TermsOfService' }">
                        Terms of Service.
                      </router-link>
                    </p>
                    <p>Artconomy is based in the United States of America</p>
                  </div>
                </v-col>
              </v-row>
            </ac-form-container>
          </ac-form>
        </v-card>
      </v-window-item>
      <v-window-item value="completed">
        <v-col v-if="selectedPlan" cols="12" class="mt-4 text-center">
          <v-icon :icon="mdiCheckCircle" size="x-large" />
          <div v-if="toFloat(selectedPlan.monthly_charge)">
            <p><strong>Your payment has been received!</strong></p>
            <p>
              We've received your payment and your account has been upgraded!
              Visit your
              <router-link
                :to="{
                  name: 'Premium',
                  params: { username: viewer!.username },
                }"
              >
                premium settings page
              </router-link>
              to view and manage your upgraded account settings.
            </p>
          </div>
          <div v-else>
            <p><strong>You're all set!</strong></p>
            <p>Thank you for using Artconomy!</p>
            <div v-if="nextUrl">
              <v-btn color="primary" :to="nextUrl" variant="flat">
                Onward!
              </v-btn>
            </div>
            <div v-else>
              <v-btn
                :to="{
                  name: 'Profile',
                  params: { username: subject!.username },
                }"
                variant="flat"
              >
                Return to my Profile
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-window-item>
    </v-window>
  </v-container>
</template>

<script setup lang="ts">
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcCardManager from "@/components/views/settings/payment/AcCardManager.vue"
import { artCall, baseCardSchema, flatten } from "@/lib/lib.ts"
import AcFormContainer from "@/components/wrappers/AcFormContainer.vue"
import AcForm from "@/components/wrappers/AcForm.vue"
import { useStripeHost } from "@/components/views/order/mixins/StripeHostMixin.ts"
import { useSubject } from "@/mixins/subjective.ts"
import { mdiCheckCircle } from "@mdi/js"
import { computed, ref, watch } from "vue"
import { useViewer } from "@/mixins/viewer.ts"
import { useSingle } from "@/store/singles/hooks.ts"
import { useForm } from "@/store/forms/hooks.ts"
import { useRoute, useRouter } from "vue-router"
import { useTheme } from "vuetify"
import type { ClientSecret, Pricing, SubjectiveProps } from "@/types/main"
import type { StaffPower, User } from "@/store/profiles/types/main"

const props = defineProps<SubjectiveProps>()
const { viewer } = useViewer()
const { subject } = useSubject({
  props,
  privateView: true,
  controlPowers: ["view_as"] as StaffPower[],
})
const route = useRoute()
const router = useRouter()
const selection = ref<null | string>(null)
const paid = ref(false)
const cardManager = ref<null | typeof AcCardManager>(null)
const { current } = useTheme()

const tab = computed(() => {
  if (selection.value === null) {
    return "selection"
  } else if (paid.value) {
    return "completed"
  } else {
    return "payment"
  }
})

const loggedInViewer = computed(() => viewer.value as User)

const pricing = useSingle<Pricing>("pricing", {
  endpoint: "/api/sales/pricing-info/",
  persist: true,
})

pricing.get()

const schema = baseCardSchema("/api/sales/premium/")
schema.fields = {
  ...schema.fields,
  card_id: { value: null },
  service: { value: null },
}
const paymentForm = useForm("serviceUpgrade", schema)

const clientSecret = useSingle<ClientSecret>("upgrade__clientSecret", {
  endpoint: "/api/sales/premium/intent/",
  params: { service: selection.value },
})

// In the future, we should refactor this to allow in-person subscriptions.
const readerFormUrl = computed(() => "#")
const canUpdate = computed(() => true)
const { updateIntent } = useStripeHost({
  clientSecret,
  readerFormUrl,
  canUpdate,
  paymentForm,
})

const plans = computed(() => {
  if (!pricing.x) {
    return []
  }
  return pricing.x.plans
})

const selectedPlan = computed(() => {
  if (!plans.value) {
    return null
  }
  return plans.value.filter((plan) => plan.name === selection.value)[0]
})

const features = computed(() => {
  const featureMap: { [key: number]: string[] } = {}
  const existingFeatures: { [key: string]: boolean } = {}
  for (const plan of plans.value) {
    const planFeatures = []
    for (const feature of plan.features) {
      if (!existingFeatures[feature]) {
        planFeatures.push(feature)
        existingFeatures[feature] = true
      }
    }
    featureMap[plan.id] = planFeatures
  }
  return featureMap
})

const setPlan = () => {
  return artCall({
    url: `/api/sales/account/${props.username}/set-plan/`,
    data: { service: selection.value },
    method: "post",
  })
}

const nonFree = computed(() => {
  return (
    selectedPlan.value &&
    (toFloat(selectedPlan.value.monthly_charge) ||
      selectedPlan.value.per_deliverable_price)
  )
})

const nextUrl = computed(() => {
  const query = route.query
  if (!(query && query.next && !Array.isArray(query.next))) {
    return false
  }
  const resolved = router.resolve(query.next)
  if (resolved.name === "NotFound") {
    return false
  }
  return resolved
})

const switchIsFree = computed(() => {
  if (!selectedPlan.value) {
    return false
  }
  if (selectedPlan.value.name === loggedInViewer.value.service_plan) {
    return true
  }
  return (
    !toFloat(selectedPlan.value.monthly_charge) &&
    !selectedPlan.value.per_deliverable_price
  )
})

const paymentSubmit = () => {
  if (
    !toFloat(selectedPlan.value!.monthly_charge) &&
    paymentForm.fields.card_id.value
  ) {
    setPlan().then(postPay)
  } else {
    cardManager.value!.stripeSubmit()
  }
}

const toFloat = (value?: string | null) => {
  return parseFloat(value || "0")
}

const postPay = () => {
  paymentForm.sending = false
  paid.value = true
}

watch(
  () => selectedPlan.value?.monthly_charge,
  (value) => {
    if (value === undefined) {
      return
    }
    if (toFloat(value)) {
      clientSecret.endpoint = `/api/sales/account/${props.username}/premium/intent/`
    } else {
      clientSecret.endpoint = `/api/sales/account/${props.username}/cards/setup-intent/`
    }
  },
)

watch(selection, (value) => {
  if (!value) {
    return
  }
  paymentForm.fields.service.update(value)
  clientSecret.params = {
    ...clientSecret.params,
    service: value,
  }
  updateIntent()
  if (switchIsFree.value) {
    paymentForm.sending = true
    setPlan().then(postPay)
  }
})
</script>

<style scoped>
.card-bottom {
  position: absolute;
  bottom: 0;
  height: 75px;
}

.service-container {
  padding-bottom: 75px;
}

.item-flatten {
  display: unset;
}
</style>
