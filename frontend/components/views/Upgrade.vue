<template>
  <v-container>
    <v-card color="grey darken-3">
      <v-card-text>
        <v-row no-gutters  >
          <v-col>
            <h1>Upgrade Your Account</h1>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <v-tabs-items v-model="tab">
      <v-tab-item value="selection">
        <ac-load-section :controller="pricing">
          <template v-slot:default>
            <v-row no-gutters   class="mt-3" v-if="selection === null">
              <v-col cols="12" md="6" offset-md="3">
                <v-card style="height: 100%">
                  <v-card-title text-center>
                    <v-col class="text-center" >
                      <v-icon>landscape</v-icon>&nbsp;Artconomy Landscape
                    </v-col>
                  </v-card-title>
                  <v-card-text class="mb-5">
                    <v-row no-gutters class="fill-height" >
                      <v-col>
                        <v-list two-line>
                          <v-list-item>
                            <v-list-item-content>
                              Receive Notifications when your favorite artists become available
                            </v-list-item-content>
                          </v-list-item>
                          <v-divider/>
                          <v-list-item>
                            <v-list-item-content>
                              Get the opportunity to try experimental new features first!
                            </v-list-item-content>
                          </v-list-item>
                          <v-divider/>
                          <v-list-item>
                            <v-list-item-content class="item-flatten">
                              Get <strong>Bonus Cash</strong> for every Shield-protected commission you complete!
                            </v-list-item-content>
                          </v-list-item>
                          <v-divider/>
                          <v-list-item>
                            <v-list-item-content>
                              ...All for ${{pricing.x.landscape_price}}/Month!
                            </v-list-item-content>
                          </v-list-item>
                        </v-list>
                      </v-col>
                    </v-row>
                  </v-card-text>
                  <v-card-text class="card-bottom text-center">
                    <v-btn color="primary" v-if="!viewer.landscape_enabled" @click="selection='landscape'">Get Landscape!
                    </v-btn>
                    <v-btn v-else :to="{name: 'Premium', params: {username: viewer.username}}">Manage
                      Landscape
                    </v-btn>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </template>
        </ac-load-section>
      </v-tab-item>
      <v-tab-item value="payment">
        <v-card>
          <ac-form @submit.prevent="paymentSubmit">
            <ac-form-container v-bind="paymentForm.bind">
              <v-row class="mt-3" v-if="selection !== null">
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
                      :client-secret="(clientSecret.x && clientSecret.x.secret) || ''"
                  />
                </v-col>
                <v-col cols="12" class="pricing-container text-center" >
                  <strong>Monthly charge: ${{price}}</strong> <br/>
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
        <v-col cols="12" class="mt-4 text-center">
          <i class="fa fa-5x fa-check-circle" /><br/>
          <p><strong>Your payment has been received!</strong></p>
          <p>We've received your payment and your account has been upgraded! Visit your
            <router-link :to="{name: 'Premium', params: {username: viewer.username}}">premium settings page</router-link>
            to view and manage your upgraded account settings.
          </p>
        </v-col>
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script lang="ts">
import Viewer from '@/mixins/viewer'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'
import Component, {mixins} from 'vue-class-component'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import {FormController} from '@/store/forms/form-controller'
import {baseCardSchema} from '@/lib/lib'
import {Watch} from 'vue-property-decorator'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import StripeHostMixin from '@/components/views/order/mixins/StripeHostMixin'
import {PROCESSORS} from '@/types/PROCESSORS'

@Component({
  components: {AcForm, AcFormContainer, AcCardManager, AcLoadSection},
})
export default class Upgrade extends mixins(Viewer, StripeHostMixin) {
    public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
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

    public get price() {
      if (!this.pricing.x) {
        return
      }
      // @ts-ignore
      return this.pricing.x[this.selection + '_price']
    }

    public get processor() {
      return window.DEFAULT_CARD_PROCESSOR
    }

    public get stripeEnabled() {
      return this.processor === PROCESSORS.STRIPE
    }

    @Watch('selection')
    public setSelection(value: string) {
      if (!value) {
        return
      }
      this.paymentForm.fields.service.update(value)
      this.updateIntent()
    }

    public paymentSubmit() {
      if (!this.stripeEnabled) {
        this.paymentForm.submitThen(this.postPay)
      }
      const cardManager = this.$refs.cardManager as any
      cardManager.stripeSubmit()
    }

    public postPay() {
      this.paid = true
    }

    public created() {
      this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/v1/pricing-info/'})
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
          params: {service: this.selection || 'landscape'},
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
