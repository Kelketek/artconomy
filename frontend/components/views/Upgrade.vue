<template>
  <v-container>
    <v-card color="grey darken-3">
      <v-card-text>
        <v-layout row wrap>
          <v-flex>
            <h1>Upgrade Your Account</h1>
            <span class="subheading">Check out our options below to enhance your art experience!</span>
          </v-flex>
        </v-layout>
      </v-card-text>
    </v-card>
    <v-tabs-items v-model="tab">
      <v-tab-item value="selection">
        <ac-load-section :controller="pricing">
          <template v-slot:default>
            <v-layout row wrap class="mt-3" v-if="selection === null">
              <v-flex xs12 md5>
                <v-card style="height: 100%" class="service-container">
                  <v-card-title>
                    <v-flex text-xs-center>
                      <v-icon>portrait</v-icon>&nbsp;Artconomy Portrait
                    </v-flex>
                  </v-card-title>
                  <v-card-text>
                    <v-layout row>
                      <v-flex>
                        <v-list>
                          <v-list-tile>Receive Notifications when your favorite artists become available</v-list-tile>
                          <v-divider/>
                          <v-list-tile>Get the opportunity to try experimental new features first!
                          </v-list-tile>
                          <v-list-tile>...for ${{pricing.x.portrait_price}}/Month!</v-list-tile>
                        </v-list>
                      </v-flex>
                    </v-layout>
                  </v-card-text>
                  <v-card-text class="card-bottom text-xs-center">
                    <v-btn color="primary" v-if="!viewer.landscape_enabled && !viewer.portrait_enabled"
                           @click="selection='portrait'">Get Portrait!
                    </v-btn>
                    <v-btn v-else :to="{name: 'Premium', params: {username: viewer.username}}">Manage
                      Portrait
                    </v-btn>
                  </v-card-text>
                </v-card>
              </v-flex>
              <v-flex xs12 md5 offset-md2>
                <v-card style="height: 100%">
                  <v-card-title text-xs-center>
                    <v-flex text-xs-center>
                      <v-icon>landscape</v-icon>&nbsp;Artconomy Landscape
                    </v-flex>
                  </v-card-title>
                  <v-card-text class="mb-5">
                    <v-layout fill-height>
                      <v-flex>
                        <v-list two-line>
                          <v-list-tile>
                            <v-list-tile-content>
                              Receive Notifications when your favorite artists become available
                            </v-list-tile-content>
                          </v-list-tile>
                          <v-divider/>
                          <v-list-tile>
                            <v-list-tile-content>
                              Get the opportunity to try experimental new features first!
                            </v-list-tile-content>
                          </v-list-tile>
                          <v-divider/>
                          <v-list-tile>
                            <v-list-tile-content>
                              Get <strong>Bonus Cash</strong> for every Shield-protected commission you complete!
                            </v-list-tile-content>
                          </v-list-tile>
                          <v-divider/>
                          <v-list-tile>
                            <v-list-tile-content>
                              ...All for ${{pricing.x.landscape_price}}/Month!
                            </v-list-tile-content>
                          </v-list-tile>
                        </v-list>
                      </v-flex>
                    </v-layout>
                  </v-card-text>
                  <v-card-text class="card-bottom text-xs-center">
                    <v-btn color="primary" v-if="!viewer.landscape_enabled" @click="selection='landscape'">Get Landscape!
                    </v-btn>
                    <v-btn v-else :to="{name: 'Premium', params: {username: viewer.username}}">Manage
                      Landscape
                    </v-btn>
                  </v-card-text>
                </v-card>
              </v-flex>
            </v-layout>
          </template>
        </ac-load-section>
      </v-tab-item>
      <v-tab-item value="payment">
        <v-card>
          <ac-form @submit.prevent="paymentForm.submitThen(postPay)">
            <ac-form-container>
              <v-layout row wrap class="mt-3" v-if="selection !== null">
                <v-flex xs12>
                  <ac-card-manager
                      ref="cardManager"
                      :payment="true"
                      :username="viewer.username"
                      :cc-form="paymentForm"
                      :field-mode="true"
                      v-model="paymentForm.fields.card_id.model"
                      :show-save="false"
                  />
                </v-flex>
                <v-flex xs12 class="pricing-container" text-xs-center>
                  <strong>Monthly charge: ${{price}}</strong> <br/>
                  <div class="mt-2 text-xs-center">
                    <v-btn @click="selection=null">Go back</v-btn>
                    <v-btn type="submit" color="primary">
                      Start Service
                    </v-btn>
                    <p>Premium services, as with all use of Artconomy's offerings, are subject to the
                      <router-link :to="{name: 'TermsOfService'}">Terms of Service.</router-link>
                    </p>
                    <p>Artconomy is based in the United States of America</p>
                  </div>
                </v-flex>
              </v-layout>
            </ac-form-container>
          </ac-form>
        </v-card>
      </v-tab-item>
      <v-tab-item value="completed">
        <v-flex xs12 text-xs-center class="mt-4">
          <i class="fa fa-5x fa-check-circle"></i><br/>
          <p><strong>Your payment has been received!</strong></p>
          <p>We've received your payment and your account has been upgraded! Visit your
            <router-link :to="{name: 'Premium', params: {username: viewer.username}}">premium settings page</router-link>
            to view and manage your upgraded account settings.
          </p>
        </v-flex>
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
import {baseCardSchema} from '@/lib'
import {Watch} from 'vue-property-decorator'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {User} from '@/store/profiles/types/User'
import AcForm from '@/components/wrappers/AcForm.vue'
  @Component({
    components: {AcForm, AcFormContainer, AcCardManager, AcLoadSection},
  })
export default class Upgrade extends mixins(Viewer) {
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

    @Watch('selection')
    public setSelection(value: string) {
      if (!value) {
        return
      }
      this.paymentForm.fields.service.update(value)
    }

    public postPay(response: User) {
      this.paid = true
      this.viewerHandler.user.setX(response)
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
</style>
