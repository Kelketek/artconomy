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
          <template v-slot:default v-if="selection === null">
            <v-row>
              <v-col cols="12" md="4" class="mt-3" v-for="(plan, index) in plans" :key="plan.id">
                <v-card style="height: 100%" :color="$vuetify.theme.current.colors['well-darken-2']"
                        class="d-flex flex-column">
                  <v-card-text>
                    <v-row>
                      <v-col class="text-center" cols="12">
                        <v-card>
                          <v-card-title class="d-block text-center">{{plan.name}}</v-card-title>
                          <v-card-text>{{plan.description}}</v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>
                  </v-card-text>
                  <v-card-text class="flex-fill align-self-baseline align-content-start">
                    <v-row class="fill-height" no-gutters>
                      <v-col cols="12">
                        <v-list two-line>
                          <v-list-item v-if="features[plan.id].length && plans.length > 1 && index !== 0">
                            <strong>...All that, plus:</strong>
                          </v-list-item>
                          <template v-for="(feature, index) in features[plan.id]" :key="feature">
                            <v-list-item>
                              {{ feature }}
                            </v-list-item>
                            <v-divider :key="`divider-${feature}`" v-if="index !== (features[plan.id].length - 1)"/>
                          </template>
                        </v-list>
                      </v-col>
                    </v-row>
                  </v-card-text>
                  <v-card-actions class="justify-center align-self-end text-center" style="width: 100%">
                    <v-row>
                      <v-col cols="12">
                        <v-card>
                          <v-card-text class="text-center">
                            <div>
                              <span class="text-h4" v-if="!plan.max_simultaneous_orders">${{plan.monthly_charge}} Monthly</span>
                              <span v-else-if="!plan.monthly_charge">
                                <span class="text-h4">FREE</span>
                              </span>
                            </div>
                            <div>Shield fee: {{plan.shield_percentage_price}}%<sup
                                v-if="pricing.x!.international_conversion_percentage">*</sup> <span
                                v-if="plan.shield_static_price">+ ${{plan.shield_static_price.toFixed(2)}}</span></div>
                            <div v-if="plan.per_deliverable_price">Non-shield order tracking fee:
                              ${{plan.per_deliverable_price.toFixed(2)}}
                            </div>
                            <div>
                              <div v-if="plan.max_simultaneous_orders">
                                Up to {{plan.max_simultaneous_orders}} order<span
                                  v-if="!(plan.max_simultaneous_orders === 1)">s</span> at a time
                              </div>
                              <div v-else-if="!plan.per_deliverable_price">
                                Track Unlimited Orders
                              </div>
                            </div>
                            <div v-if="pricing.x!.international_conversion_percentage">
                              <sup>* Transfers outside the US include an additional
                                {{pricing.x!.international_conversion_percentage}}% conversion fee.</sup>
                            </div>
                          </v-card-text>
                        </v-card>
                      </v-col>
                      <v-col cols="12">
                        <v-chip color="gray" variant="flat" light
                                v-if="plan.name === loggedInViewer.next_service_plan && !plan.monthly_charge"><strong>Your
                          Current Plan</strong></v-chip>
                        <template v-else>
                          <v-btn color="primary" variant="flat" v-if="!(plan.name === loggedInViewer.next_service_plan)"
                                 @click="selection=plan.name">
                            Switch to {{ plan.name }}!
                          </v-btn>
                          <v-btn v-else :to="{name: 'Premium', params: {username: viewer!.username}}" variant="flat">Manage {{
                            plan.name }}
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
              <v-row class="mt-3" v-if="selection">
                <v-col cols="12">
                  <ac-card-manager
                      ref="cardManager"
                      :payment="true"
                      :username="viewer!.username"
                      :cc-form="paymentForm"
                      :field-mode="true"
                      v-model="paymentForm.fields.card_id.model"
                      :show-save="false"
                      :processor="processor"
                      @paymentSent="postPay"
                      @cardAdded="setPlan"
                      :save-only="!selectedPlan.monthly_charge"
                      :client-secret="(clientSecret.x && clientSecret.x.secret) || ''"
                  />
                </v-col>
                <v-col cols="12" class="pricing-container text-center">
                  <strong>Monthly charge: ${{selectedPlan.monthly_charge}}</strong> <br/>
                  <div v-if="selectedPlan.per_deliverable_price">
                    Any orders tracked which aren't covered by shield protection will be billed at
                    ${{selectedPlan.per_deliverable_price.toFixed(2)}} at the end of your billing cycle.
                  </div>
                  <div class="mt-2 text-center">
                    <v-btn @click="selection=null" class="mx-1" variant="flat">Go back</v-btn>
                    <v-btn type="submit" color="primary" class="mx-1" variant="flat">
                      Start Service
                    </v-btn>
                    <p>Premium services, as with all use of Artconomy's offerings, are subject to the
                      <router-link :to="{name: 'TermsOfService'}">Terms of Service.</router-link>
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
        <v-col cols="12" class="mt-4 text-center" v-if="selectedPlan">
          <v-icon :icon="mdiCheckCircle" size="x-large" />
          <div v-if="selectedPlan.monthly_charge">
            <p><strong>Your payment has been received!</strong></p>
            <p>We've received your payment and your account has been upgraded! Visit your
              <router-link :to="{name: 'Premium', params: {username: viewer!.username}}">premium settings page
              </router-link>
              to view and manage your upgraded account settings.
            </p>
          </div>
          <div v-else>
            <p><strong>You're all set!</strong></p>
            <p>Thank you for using Artconomy!</p>
            <div v-if="nextUrl">
              <v-btn color="primary" :to="nextUrl" variant="flat">Onward!</v-btn>
            </div>
            <div v-else>
              <v-btn :to="{name: 'Profile', params: {username: subject!.username}}" variant="flat">Return to my Profile</v-btn>
            </div>
          </div>
        </v-col>
      </v-window-item>
    </v-window>
  </v-container>
</template>

<script lang="ts">
import {Component, mixins, toNative, Watch} from 'vue-facing-decorator'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import {FormController} from '@/store/forms/form-controller.ts'
import {artCall, baseCardSchema} from '@/lib/lib.ts'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import StripeHostMixin from '@/components/views/order/mixins/StripeHostMixin.ts'
import Formatting from '@/mixins/formatting.ts'
import Subjective from '@/mixins/subjective.ts'
import {User} from '@/store/profiles/types/User.ts'
import {SingleController} from '@/store/singles/controller.ts'
import Pricing from '@/types/Pricing.ts'
import {mdiCheckCircle} from '@mdi/js'

@Component({
  components: {
    AcForm,
    AcFormContainer,
    AcCardManager,
    AcLoadSection,
  },
})
class Upgrade extends mixins(Subjective, StripeHostMixin, Formatting) {
  public privateView = true
  public pricing = null as unknown as SingleController<Pricing>
  public paymentForm = null as unknown as FormController
  public selection: null | string = null
  public paid = false
  public mdiCheckCircle = mdiCheckCircle

  public get tab() {
    if (this.selection === null) {
      return 'selection'
    } else if (this.paid) {
      return 'completed'
    } else {
      return 'payment'
    }
  }

  public get loggedInViewer(): User {
    return this.viewer as User
  }

  public get processor() {
    return window.DEFAULT_CARD_PROCESSOR
  }

  public get readerFormUrl() {
    // TODO: Refactor to use standard invoices so we can return a URL here and subscribe someone in person,
    //  if we wanted.
    return '#'
  }

  public get selectedPlan() {
    if (!this.plans) {
      return null
    }
    return this.plans.filter((plan) => plan.name === this.selection)[0]
  }

  public get plans() {
    if (!(this.pricing && this.pricing.x)) {
      return []
    }
    return this.pricing.x.plans
  }

  public get features() {
    const featureMap: { [key: number]: string[] } = {}
    const existingFeatures: { [key: string]: boolean } = {}
    for (const plan of this.plans) {
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
  }

  public setPlan() {
    return artCall({
      url: `/api/sales/account/${this.username}/set-plan/`,
      data: {service: this.selection},
      method: 'post',
    })
  }

  public get nonFree() {
    return this.selectedPlan && (this.selectedPlan.monthly_charge || this.selectedPlan.per_deliverable_price)
  }

  @Watch('selectedPlan.monthly_charge')
  public setEndpoint(value: undefined | number) {
    if (value === undefined) {
      return
    }
    if (!value) {
      this.clientSecret.endpoint = `/api/sales/account/${this.username}/cards/setup-intent/`
    } else {
      this.clientSecret.endpoint = `/api/sales/account/${this.username}/premium/intent/`
    }
  }

  public get nextUrl() {
    const query = this.$route.query
    if (!(query && query.next && !Array.isArray(query.next))) {
      return false
    }
    const resolved = this.$router.resolve(query.next)
    if (resolved.name === 'NotFound') {
      return false
    }
    return resolved
  }

  public get switchIsFree() {
    if (!this.selectedPlan) {
      return false
    }
    if (this.selectedPlan.name === (this.viewer as User).service_plan) {
      return true
    }
    return !this.selectedPlan.monthly_charge && !this.selectedPlan.per_deliverable_price
  }

  @Watch('selection')
  public setSelection(value: string) {
    if (!value) {
      return
    }
    this.paymentForm.fields.service.update(value)
    this.clientSecret.params = {
      ...this.clientSecret.params,
      service: value,
    }
    this.updateIntent()
    if (this.switchIsFree) {
      this.paymentForm.sending = true
      this.setPlan().then(this.postPay)
    }
  }

  public paymentSubmit() {
    const cardManager = this.$refs.cardManager as any
    if (!this.selectedPlan!.monthly_charge && this.paymentForm.fields.card_id.value) {
      this.setPlan().then(this.postPay)
    } else {
      cardManager.stripeSubmit()
    }
  }

  public postPay() {
    this.paymentForm.sending = false
    this.paid = true
  }

  public created() {
    // @ts-ignore
    window.payment = this
    this.pricing = this.$getSingle('pricing', {
      endpoint: '/api/sales/pricing-info/',
      persist: true,
    })
    this.pricing.get()
    const schema = baseCardSchema('/api/sales/premium/')
    schema.fields = {
      ...schema.fields,
      card_id: {value: null},
      service: {value: null},
    }
    this.paymentForm = this.$getForm('serviceUpgrade', schema)
    this.clientSecret = this.$getSingle(
        'upgrade__clientSecret', {
          endpoint: '/api/sales/premium/intent/',
          params: {service: this.selection},
        })
  }
}

export default toNative(Upgrade)
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
