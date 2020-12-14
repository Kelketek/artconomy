<template>
  <ac-load-section :controller="product">
    <template v-slot:default>
      <v-row>
        <v-col cols="12" md="8" offset-lg="1" >
          <ac-form @submit.prevent="orderForm.submitThen(goToOrder)">
            <ac-form-container
                :errors="orderForm.errors"
                :sending="orderForm.sending"
            >
              <v-card>
                <v-toolbar v-if="isRegistered" dense color="black">
                  <ac-avatar :user="viewer" :show-name="false" />
                  <v-toolbar-title class="ml-1">{{viewerName}}</v-toolbar-title>
                </v-toolbar>
                <v-card-title>
                  <span class="title">New Commission Order</span>
                </v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="12" sm="6" v-if="!isRegistered">
                      <v-subheader>Checkout as Guest</v-subheader>
                      <ac-bound-field label="Email" v-if="!isRegistered" :field="orderForm.fields.email" />
                    </v-col>
                    <v-col cols="12" sm="6" class="text-center" v-if="!isRegistered">
                      <p>Or, if you have an account,</p>
                      <v-btn :to="{name: 'Login', params: {tabName: 'login'}, query: {next: $route.fullPath}}" color="primary">Log in here!</v-btn>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12">
                      <ac-bound-field
                          label="Content Rating of Piece"
                          field-type="ac-rating-field" :field="orderForm.fields.rating"
                          :persistent-hint="true"
                          hint="Please select the desired content rating of the piece you are commissioning."
                      />
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12" v-if="isRegistered">
                      <ac-bound-field
                          field-type="ac-character-select" :field="orderForm.fields.characters" label="Characters"
                          hint="Start typing a character's name to search. If you've set up characters on Artconomy, you can
                  attach them to this order for easy referencing by the artist! If you haven't added any characters, or
                  no characters are in this piece, you may leave this blank."
                          v-if="showCharacters"
                          :init-items="initCharacters"
                      />
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12" sm="6" class="pt-3" order="2" order-sm="1">
                      <ac-bound-field
                          :field="orderForm.fields.details" field-type="ac-editor" label="Description"
                          :rows="7"
                          :save-indicator="false"
                      />
                    </v-col>
                    <v-col cols="12" sm="6" order="1" order-sm="2">
                      <v-row>
                        <v-col class="d-flex justify-content justify-center align-content-center" cols="3" style="flex-direction: column">
                          <v-img src="/static/images/laptop.png" max-height="30vh" :contain="true" />
                        </v-col>
                        <v-col cols="9">
                          <v-subheader>Example description</v-subheader>
                            Vulpy:<br />
                            * is a fox<br />
                            * is about three feet tall<br />
                            * has orange fur, with white on his belly, cheeks, 'socks', and inner ears<br />
                            * has a paintbrush tail that can be any color, but is black for this piece.<br />
                            * has pink pawpads<br /><br />
                            Please draw Vulpy sitting and typing away excitedly on a computer!
                        </v-col>
                      </v-row>
                    </v-col>
                  </v-row>
                  <v-row no-gutters  >
                    <v-col cols="12">
                      <ac-load-section :controller="subjectHandler.artistProfile">
                        <template v-slot:default>
                          <v-subheader v-if="subjectHandler.artistProfile.x.commission_info">Commission Info</v-subheader>
                          <ac-rendered :value="subjectHandler.artistProfile.x.commission_info" :truncate="500" />
                        </template>
                      </ac-load-section>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12" sm="6">
                      <ac-bound-field
                          field-type="ac-checkbox" :field="orderForm.fields.private" label="Private Order" :persistent-hint="true"
                          hint="Hides the resulting submission from public view and tells the artist you want this commission
                    to be private. The artist may charge an additional fee, since they will not be able to use the piece
                    in their portfolio."
                      />
                    </v-col>
                    <v-col class="text-center" cols="12" sm="6" align-self="center">
                      <h3>All orders are bound by the
                        <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement.</router-link>
                      </h3>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12">
                      <v-alert type="warning" :value="true" v-if="product.x.wait_list">
                        This order will be waitlisted. Waitlisted orders are not guaranteed to be accepted on any
                        particular time table and may not be fulfilled in the order they are received. Please check the
                        product description for further details or contact the artist if there is any confusion.
                        <strong>You will not be expected to pay for this order unless and until it is accepted.</strong>
                      </v-alert>
                      <v-alert type="info" :value="true">
                        Once your order is placed, the artist will review your request, make any adjustments to the quote as needed, and present them for your approval and payment. We will update you via email as things progress.
                        <strong>You will have the opportunity to attach additional reference images after the order is placed.</strong>
                      </v-alert>
                    </v-col>
                    <v-col class="text-center" cols="12" >
                      <v-btn color="primary" type="submit" id="place-order-button">Place Order</v-btn>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </ac-form-container>
          </ac-form>
        </v-col>
        <v-col cols="12" offset-md="1" md="3" lg="2">
          <v-toolbar dense color="black">
            <ac-avatar :user="product.x.user" :show-name="false" />
            <v-toolbar-title class="ml-1"><ac-link :to="profileLink(product.x.user)">{{username}}</ac-link></v-toolbar-title>
          </v-toolbar>
          <v-card :color="$vuetify.theme.currentTheme.darkBase.darken2">
            <v-card-text>
              <v-row dense>
                <v-col class="title" cols="12" >
                  Order Summary
                </v-col>
                <v-col class="subheading" cols="12" >
                  {{product.x.name}}
                </v-col>
                <v-col cols="12">
                  <ac-asset :asset="product.x.primary_submission" thumb-name="thumbnail" />
                </v-col>
                <v-col class="subtitle-1" cols="12">
                  Starts at ${{product.x.starting_price.toFixed(2)}}
                </v-col>
                <v-col>
                  <span v-if="product.x.revisions">
                    <strong>{{product.x.revisions}}</strong> revision<span v-if="product.x.revisions > 1">s</span> included.
                  </span>
                </v-col>
                <v-col cols="12">
                  <span>Estimated completion: <strong>{{formatDateTerse(deliveryDate)}}</strong></span>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
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
import AcLink from '@/components/wrappers/AcLink.vue'
import Product from '@/types/Product'
import {artCall} from '@/lib/lib'
import {Character} from '@/store/characters/types/Character'
  @Component({
    components: {
      AcLink,
      AcForm,
      AcRendered,
      AcFormContainer,
      AcAvatar,
      AcAsset,
      AcBoundField,
      AcLoadSection,
      AcFormDialog,
    },
  })
export default class NewOrder extends mixins(ProductCentric, Formatting) {
    public orderForm: FormController = null as unknown as FormController
    public loginForm: FormController = null as unknown as FormController
    public initCharacters: Character[] = []
    public showCharacters = false

    @Watch('viewer.guest_email')
    public updateEmail(newVal: string) {
      if (!newVal) {
        this.orderForm.fields.email.update('', false)
        return
      }
      this.orderForm.fields.email.update(newVal)
    }

    public sendEvent() {
      const product = this.product.x as Product
      window.pintrk(
        'track',
        'checkout', {
          value: product.starting_price,
          order_quantity: 1,
          currency: 'USD',
          line_items: [
            {
              product_id: product.id,
            },
          ],
        })
    }

    public goToOrder(order: Order) {
      // Could take a while. Let's not make it look like we're done.
      this.orderForm.sending = true
      const link = {...order.default_path}
      link.query = {...link.query, showConfirm: 'true'}
      if (!this.isRegistered) {
        link.params!.username = this.rawViewerName
        this.viewerHandler.refresh().then(() => {
          this.$router.push(link)
          this.sendEvent()
          this.orderForm.sending = false
        })
        return
      }
      this.sendEvent()
      this.$router.push(link)
      this.orderForm.sending = false
    }

    public created() {
      // The way we're constructed allows us to avoid refetching if we arrive through the product page, but
      // leaves us in the same scroll position as we were. Fix that here.
      window.scrollTo(0, 0)
      this.product.get()
      const viewer = this.viewer as User
      this.orderForm = this.$getForm('newOrder', {
        endpoint: this.product.endpoint + 'order/',
        persistent: true,
        fields: {
          email: {value: (viewer.guest_email || ''), validators: [{name: 'email'}]},
          private: {value: false},
          characters: {value: []},
          rating: {value: 0, validators: [{name: 'artistRating', async: true, args: [this.username]}]},
          details: {value: ''},
        },
      })
      this.subjectHandler.artistProfile.get().then()
      if (this.orderForm.fields.characters.value.length === 0) {
        this.showCharacters = true
      } else {
        const promises = []
        for (const charId of this.orderForm.fields.characters.model) {
          promises.push(artCall({url: `/api/profiles/v1/data/character/id/${charId}/`, method: 'get'}).then(
            (response) => this.initCharacters.push(response),
          ).catch(() => {
            this.orderForm.fields.characters.model = this.orderForm.fields.characters.model.filter(
              (val: number) => val !== charId,
            )
          }))
        }
        Promise.all(promises).then(() => { this.showCharacters = true })
      }
    }
}
</script>
