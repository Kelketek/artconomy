<template>
  <ac-load-section :controller="product">
    <template v-slot:default>
      <v-layout row wrap class="ma-2">
        <v-flex xs12 md8 offset-lg1 pb-3>
          <ac-form @submit.prevent="orderForm.submitThen(goToOrder)">
            <ac-form-container
                :errors="orderForm.errors"
                :sending="orderForm.sending"
            >
              <v-card>
                <v-toolbar v-if="isRegistered" dense>
                  <ac-avatar :user="viewer" :show-name="false"></ac-avatar>
                  <v-toolbar-title>{{viewerName}}</v-toolbar-title>
                </v-toolbar>
                <v-card-title>
                  <span class="title">New Commission Order</span>
                </v-card-title>
                <v-card-text>
                  <v-layout row wrap>
                    <v-flex xs12 sm6 v-if="!isRegistered">
                      <v-subheader>Checkout as Guest</v-subheader>
                      <ac-bound-field label="Email" v-if="!isRegistered" :field="orderForm.fields.email" />
                    </v-flex>
                    <v-flex xs12 sm6 text-xs-center class="pa-2" v-if="!isRegistered">
                      <p>Or, if you have an account,</p>
                      <v-btn :to="{name: 'Login', params: {tabName: 'login'}, query: {next: $route.fullPath}}" color="primary">Log in here!</v-btn>
                    </v-flex>
                  </v-layout>
                  <v-layout row wrap>
                    <v-flex xs12>
                      <ac-bound-field
                          label="Content Rating of Piece"
                          field-type="ac-rating-field" :field="orderForm.fields.rating"
                          :persistent-hint="true"
                          hint="Please select the desired content rating of the piece you are commissioning."
                      ></ac-bound-field>
                    </v-flex>
                  </v-layout>
                  <v-layout row wrap>
                    <v-flex xs12 v-if="isRegistered">
                      <ac-bound-field
                          field-type="ac-character-select" :field="orderForm.fields.characters" label="Characters"
                          hint="Start typing a character's name to search. If you've set up characters on Artconomy, you can
                  attach them to this order for easy referencing by the artist! If you haven't added any characters, or
                  no characters are in this piece, you may leave this blank." />
                    </v-flex>
                  </v-layout>
                  <v-layout row wrap>
                    <v-flex xs12 sm6 class="pt-3" order-xs2 order-sm1>
                      <ac-bound-field
                          :field="orderForm.fields.details" field-type="ac-editor" label="Description"
                          :rows="7"
                          :save-indicator="false"
                      ></ac-bound-field>
                    </v-flex>
                    <v-flex xs12 sm6 order-xs1 order-sm2>
                      <v-layout row wrap>
                        <v-flex xs3 d-flex justify-content justify-center align-content-center style="flex-direction: column">
                          <v-img src="/static/images/laptop.png" max-height="30vh" :contain="true" />
                        </v-flex>
                        <v-flex xs9>
                          <v-subheader>Example description</v-subheader>
                            Vulpy:<br />
                            * is a fox<br />
                            * is about three feet tall<br />
                            * has orange fur, with white on his belly, cheeks, 'socks', and inner ears<br />
                            * has a paintbrush tail that can be any color, but is black for this piece.<br />
                            * has pink pawpads<br /><br />
                            Please draw Vulpy sitting and typing away excitedly on a computer!
                        </v-flex>
                      </v-layout>
                    </v-flex>
                  </v-layout>
                  <v-layout row wrap>
                    <v-flex xs12>
                      <ac-load-section :controller="subjectHandler.artistProfile">
                        <template v-slot:default>
                          <v-subheader v-if="subjectHandler.artistProfile.x.commission_info">Commission Info</v-subheader>
                          <ac-rendered :value="subjectHandler.artistProfile.x.commission_info" :truncate="500"></ac-rendered>
                        </template>
                      </ac-load-section>
                    </v-flex>
                  </v-layout>
                  <v-layout row wrap>
                    <v-flex xs12 sm6>
                      <ac-bound-field
                          field-type="v-checkbox" :field="orderForm.fields.private" label="Private Order" :persistent-hint="true"
                          hint="Hides the resulting submission from public view and tells the artist you want this commission
                    to be private. The artist may charge an additional fee, since they will not be able to use the piece
                    in their portfolio."
                      />
                    </v-flex>
                    <v-flex text-xs-center xs12 sm6>
                      <h3>All orders are bound by the
                        <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement.</router-link>
                      </h3>
                    </v-flex>
                  </v-layout>
                  <v-layout row wrap>
                    <v-flex xs12 text-xs-center>
                      <v-btn color="primary" type="submit">Place Order</v-btn>
                    </v-flex>
                  </v-layout>
                </v-card-text>
              </v-card>
            </ac-form-container>
          </ac-form>
        </v-flex>
        <v-flex xs12 offset-md1 md3 lg2>
          <v-toolbar dense>
            <ac-avatar :user="product.x.user" :show-name="false"></ac-avatar>
            <v-toolbar-title>{{username}}</v-toolbar-title>
          </v-toolbar>
          <v-card :color="$vuetify.theme.darkBase.darken2">
            <v-card-text>
              <v-layout row wrap>
                <v-flex xs12 title>
                  Order Summary
                </v-flex>
                <v-flex xs12 py-2 subheading>
                  {{product.x.name}}
                </v-flex>
                <v-flex xs12>
                  <ac-asset :asset="product.x.primary_submission" thumb-name="thumbnail"></ac-asset>
                </v-flex>
                <v-flex subheading class="py-2">
                  Starts at ${{product.x.price.toFixed(2)}}
                </v-flex>
                <v-flex>
                  <p v-if="product.x.revisions">
                    <strong>{{product.x.revisions}}</strong> revision<span v-if="product.x.revisions > 1">s</span> included.
                  </p>
                  <p>Estimated completion: <strong>{{formatDateTerse(deliveryDate)}}</strong></p>
                </v-flex>
              </v-layout>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {FormController} from '@/store/forms/form-controller'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import ProductCentric from '@/components/views/product/mixins/ProductCentric'
import AcAsset from '@/components/AcAsset.vue'
import Formatting from '@/mixins/formatting'
import AcAvatar from '@/components/AcAvatar.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import Order from '@/types/Order'
import {User} from '@/store/profiles/types/User'
import {Watch} from 'vue-property-decorator'
import AcRendered from '@/components/wrappers/AcRendered'
import AcForm from '@/components/wrappers/AcForm.vue'
  @Component({
    components: {AcForm, AcRendered, AcFormContainer, AcAvatar, AcAsset, AcBoundField, AcLoadSection, AcFormDialog},
  })
export default class NewOrder extends mixins(ProductCentric, Formatting) {
    public orderForm: FormController = null as unknown as FormController
    public loginForm: FormController = null as unknown as FormController

    @Watch('viewer.guest_email')
    public updateEmail(newVal: string) {
      if (!newVal) {
        this.orderForm.fields.email.update('', false)
        return
      }
      this.orderForm.fields.email.update(newVal)
    }

    public goToOrder(order: Order) {
      // Could take a while. Let's not make it look like we're done.
      this.orderForm.sending = true
      if (!this.isRegistered) {
        this.viewerHandler.refresh().then(() => {
          this.$router.push({name: 'Order', params: {orderId: order.id + '', username: this.rawViewerName}})
        })
        return
      }
      this.$router.push({
        name: 'Order', params: {username: this.rawViewerName, orderId: order.id + ''}, query: {showConfirm: 'true'},
      })
    }

    public created() {
      // The way we're constructed allows us to avoid refetching if we arrive through the product page, but
      // leaves us in the same scroll position as we were. Fix that here.
      window.scrollTo(0, 0)
      this.product.get()
      const viewer = this.viewer as User
      this.orderForm = this.$getForm(`product${this.productId}__order`, {
        endpoint: this.product.endpoint + 'order/',
        fields: {
          email: {value: (viewer.guest_email || ''), validators: [{name: 'email'}]},
          private: {value: false},
          characters: {value: []},
          rating: {value: 0, validators: [{name: 'artistRating', async: true, args: [this.username]}]},
          details: {value: ''},
        },
      })
      this.subjectHandler.artistProfile.get().then()
    }
}
</script>
