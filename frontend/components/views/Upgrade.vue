<template>
  <v-container>
    <v-card color="grey darken-3">
      <v-card-text>
        <v-row no-gutters>
          <v-col>
            <h1>Upgrade Your Account</h1>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <v-tabs-items v-model="tab">
      <v-tab-item value="selection">
        <ac-load-section :controller="pricing">
          <template v-slot:default v-if="selection === null">
            <v-row>
              <v-col cols="12" md="4" class="mt-3" v-for="plan in pricing.list" :key="plan.x.id">
                <v-card style="height: 100%" :color="$vuetify.theme.currentTheme.darkBase.darken2" class="d-flex flex-column">
                  <v-card-text>
                    <v-row>
                      <v-col class="text-center" cols="12">
                        <v-card>
                          <v-card-title class="d-block text-center">{{plan.x.name}}</v-card-title>
                          <v-card-text>{{plan.x.description}}</v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>
                  </v-card-text>
                  <v-card-text class="flex-fill align-self-baseline align-content-start">
                    <v-row class="fill-height" no-gutters>
                      <v-col cols="12">
                        <v-list two-line>
                          <template v-for="(feature, index) in plan.x.features">
                            <v-list-item :key="feature">
                              <v-list-item-content>
                                {{ feature }}
                              </v-list-item-content>
                            </v-list-item>
                            <v-divider :key="`divider-${feature}`" v-if="index !== (plan.x.features.length - 1)"/>
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
                              <span class="text-h3" v-if="!plan.x.max_simultaneous_orders">${{plan.x.monthly_charge}} Monthly</span>
                              <span v-else-if="!plan.x.monthly_charge">
                                <span class="text-h3">FREE</span>
                              </span>
                            </div>
                            <div>Shield fee: {{plan.x.shield_percentage_price}}% <span v-if="plan.x.shield_static_price">+ ${{plan.x.shield_static_price.toFixed(2)}}</span></div>
                            <div v-if="plan.x.per_deliverable_price">Non-shield order tracking fee: ${{plan.x.per_deliverable_price.toFixed(2)}}</div>
                            <div>
                              <div v-if="plan.x.max_simultaneous_orders">
                                Up to {{plan.x.max_simultaneous_orders}} order<span v-if="!(plan.x.max_simultaneous_orders === 1)">s</span> per month
                              </div>
                            </div>
                          </v-card-text>
                        </v-card>
                      </v-col>
                      <v-col cols="12">
                        <v-chip color="gray" light v-if="plan.x.name === viewer.next_service_plan && !plan.x.monthly_charge"><strong>Your Current Plan</strong></v-chip>
                        <template v-else>
                          <v-btn color="primary" v-if="!(plan.x.name === viewer.next_service_plan)" @click="selection=plan.x.name">
                            Switch to {{ plan.x.name }}!
                          </v-btn>
                          <v-btn v-else :to="{name: 'Premium', params: {username: viewer.username}}">Manage {{  plan.x.name }}</v-btn>
                        </template>
                      </v-col>
                    </v-row>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>
          </template>
        </ac-load-section>
      </v-tab-item>
      <v-tab-item value="payment">
        <v-card v-if="selectedPlan && nonFree">
          <ac-form @submit.prevent="paymentSubmit">
            <ac-form-container v-bind="paymentForm.bind">
              <v-row class="mt-3" v-if="selection">
                <v-col cols="12">
                  <ac-card-manager
                      ref="cardManager"
                      :payment="true"
                      :username="viewer.username"
                      :cc-form="paymentForm"
                      :field-mode="true"
                      v-model="paymentForm.fields.card_id.model"
                      :show-save="false"
                      :processor="processor"
                      @paymentSent="postPay"
                      @cardAdded="setPlan"
                      :save-only="!selectedPlan.x.monthly_charge"
                      :client-secret="(clientSecret.x && clientSecret.x.secret) || ''"
                  />
                </v-col>
                <v-col cols="12" class="pricing-container text-center" >
                  <strong>Monthly charge: ${{selectedPlan.x.monthly_charge}}</strong> <br/>
                  <div class="mt-2 text-center">
                    <v-btn @click="selection=null" class="mx-1">Go back</v-btn>
                    <v-btn type="submit" color="primary" class="mx-1">
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
      </v-tab-item>
      <v-tab-item value="completed">
        <v-col cols="12" class="mt-4 text-center" v-if="selectedPlan">
          <i class="fa fa-5x fa-check-circle" /><br/>
          <div v-if="selectedPlan.x.monthly_charge">
            <p><strong>Your payment has been received!</strong></p>
            <p>We've received your payment and your account has been upgraded! Visit your
              <router-link :to="{name: 'Premium', params: {username: viewer.username}}">premium settings page</router-link>
              to view and manage your upgraded account settings.
            </p>
          </div>
          <div v-else>
            <p><strong>You're all set!</strong></p>
            <p>Thank you for using Artconomy!</p>
            <p><v-btn :to="{name: 'Profile', params: {username: subject.username}}">Return to my Profile</v-btn></p>
          </div>
        </v-col>
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import {FormController} from '@/store/forms/form-controller'
import {baseCardSchema, artCall} from '@/lib/lib'
import {Watch} from 'vue-property-decorator'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import StripeHostMixin from '@/components/views/order/mixins/StripeHostMixin'
import {ListController} from '@/store/lists/controller'
import {ServicePlan} from '@/types/ServicePlan'
import Formatting from '@/mixins/formatting'
import Subjective from '@/mixins/subjective'
import {User} from '@/store/profiles/types/User'

@Component({
  components: {AcForm, AcFormContainer, AcCardManager, AcLoadSection},
})
export default class Upgrade extends mixins(Subjective, StripeHostMixin, Formatting) {
  public pricing: ListController<ServicePlan> = null as unknown as ListController<ServicePlan>
  public paymentForm: FormController = null as unknown as FormController
  public selection: null|string = null
  public paid = false

  public get tab() {
    if (this.selection === null) {
      return 'selection'
    } else if (this.paid) {
      return 'completed'
    } else {
      return 'payment'
    }
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
    if (!this.pricing) {
      return undefined
    }
    return this.pricing.list.filter((plan) => plan.x!.name === this.selection)[0]
  }

  public setPlan() {
    return artCall({
      url: `/api/sales/v1/account/${this.username}/set-plan/`,
      data: {service: this.selection},
      method: 'post',
    })
  }

  public get nonFree() {
    return this.selectedPlan && (this.selectedPlan.x!.monthly_charge || this.selectedPlan.x!.per_deliverable_price)
  }

  @Watch('selectedPlan.x.monthly_charge')
  public setEndpoint(value: undefined|number) {
    if (value === undefined) {
      return
    }
    if (!value) {
      this.clientSecret.endpoint = `/api/sales/v1/account/${this.username}/cards/setup-intent/`
    } else {
      this.clientSecret.endpoint = `/api/sales/v1/account/${this.username}/premium/intent/`
    }
  }

  public get switchIsFree() {
    if (!this.selectedPlan) {
      return false
    }
    if (this.selectedPlan!.x!.name === (this.viewer as User).service_plan) {
      return true
    }
    return !this.selectedPlan!.x!.monthly_charge && !this.selectedPlan!.x!.per_deliverable_price
  }

  @Watch('selection')
  public setSelection(value: string) {
    if (!value) {
      return
    }
    this.paymentForm.fields.service.update(value)
    this.clientSecret.params = {...this.clientSecret.params, service: value}
    this.updateIntent()
    if (this.switchIsFree) {
      this.paymentForm.sending = true
      this.setPlan().then(this.postPay)
    }
  }

  public paymentSubmit() {
    const cardManager = this.$refs.cardManager as any
    if (!this.selectedPlan!.x!.monthly_charge && this.paymentForm.fields.card_id.value) {
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
    this.pricing = this.$getList('plans', {endpoint: '/api/sales/v1/service-plans/', paginated: false})
    this.pricing.get()
    const schema = baseCardSchema('/api/sales/v1/premium/')
    schema.fields = {
      ...schema.fields,
      card_id: {value: null},
      service: {value: null},
    }
    this.paymentForm = this.$getForm('serviceUpgrade', schema)
    this.clientSecret = this.$getSingle(
      'upgrade__clientSecret', {
        endpoint: '/api/sales/v1/premium/intent/',
        params: {service: this.selection},
      })
  }
}
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
