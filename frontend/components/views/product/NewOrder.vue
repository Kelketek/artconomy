<template>
  <ac-load-section :controller="product">
    <template v-slot:default>
      <v-row @click="() => clickCounter += 1" v-if="product.x">
        <v-col cols="12" md="8" offset-lg="1">
          <ac-form @submit.prevent="submitAction">
            <ac-form-container
                :errors="orderForm.errors"
                :sending="orderForm.sending"
            >
              <template v-slot:top-buttons/>
              <v-card>
                <v-card-title>
                  <span class="title">New Commission Order</span>
                </v-card-title>
                <v-toolbar v-if="isRegistered" dense color="black">
                  <ac-avatar :user="viewer" :show-name="false" class="ml-3"/>
                  <v-toolbar-title class="ml-1">{{viewerName}}</v-toolbar-title>
                </v-toolbar>
                <v-stepper v-model="orderForm.step" class="submission-stepper" non-linear>
                  <v-stepper-header>
                    <v-stepper-item :complete="orderForm.steps[1].complete" :value="1"
                                    :rules="orderForm.steps[1].rules">Basics
                    </v-stepper-item>
                    <v-divider/>
                    <v-stepper-item :value="2" :rules="orderForm.steps[2].rules"
                                    :complete="orderForm.steps[1].complete">Details
                    </v-stepper-item>
                    <v-divider/>
                    <v-stepper-item :value="3" :rules="orderForm.steps[3].rules">Notices and Agreements</v-stepper-item>
                  </v-stepper-header>
                  <v-stepper-window>
                    <v-stepper-window-item :value="1">
                      <v-row>
                        <v-col cols="12" sm="6" v-if="invoicing || !isRegistered || product.x.table_product">
                          <v-list-subheader v-if="!isRegistered">Checkout as Guest</v-list-subheader>
                          <v-list-subheader v-if="invoicing">Enter customer's username or email</v-list-subheader>
                          <v-list-subheader v-else-if="product.x.table_product">Enter Commissioner's Email
                          </v-list-subheader>
                          <ac-bound-field
                              label="Customer username/email"
                              :field="orderForm.fields.email"
                              item-value="username"
                              :multiple="false"
                              :allow-raw="true"
                              v-if="invoicing"
                              hint="Enter the username or the email address of the customer this commission is for.
                This can be left blank if you only want to use this order for tracking purposes."
                          />
                          <ac-bound-field label="Email" v-else :field="orderForm.fields.email"/>
                        </v-col>
                        <v-col cols="12" sm="6" class="text-center" v-if="!isRegistered">
                          <p>Or, if you have an account,</p>
                          <v-btn :to="{name: 'Login', query: {next: $route.fullPath}}" color="primary" variant="flat">Log in here!
                          </v-btn>
                        </v-col>
                      </v-row>
                      <v-row v-if="product.x.max_rating > 0">
                        <v-col cols="12">
                          <ac-bound-field
                              label="Content Ratings of Piece"
                              field-type="ac-rating-field" :field="orderForm.fields.rating"
                              :persistent-hint="true"
                              :max="product.x.max_rating"
                          />
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="12" v-if="isRegistered && !product.x.table_product">
                          <ac-bound-field
                              field-type="ac-character-select" :field="orderForm.fields.characters" label="Characters"
                              hint="Start typing a character's name to search. If you've set up characters on Artconomy, you can
                  attach them to this order for easy referencing by the artist! If you haven't added any characters, or
                  no characters are in this piece, you may leave this blank."
                              v-if="showCharacters"
                              autocomplete="off"
                              :init-items="initCharacters"
                          />
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="12" sm="6">
                          <ac-bound-field
                              field-type="ac-checkbox" :field="orderForm.fields.private" label="Private Order"
                              :persistent-hint="true"
                              :hint="privateHint"
                          />
                        </v-col>
                        <v-col cols="12" sm="6" v-if="product.x.name_your_price">
                          <ac-bound-field
                              field-type="ac-price-field" :field="orderForm.fields.named_price" label="Price"
                              :persistent-hint="true"
                              :hint="`Enter the price you'd like to pay for this work.${currentPrice && ` Must be at least ${currentPrice.toFixed(2)} to cover the artist's costs.`}`"
                          />
                        </v-col>
                      </v-row>
                    </v-stepper-window-item>
                    <v-stepper-window-item :value="2">
                      <v-row class="justify-center">
                        <v-col cols="12" sm="6" order="2" order-sm="1" class="align-self-center pt-5">
                          <ac-bound-field
                              :field="orderForm.fields.details" field-type="ac-editor" label="Description"
                              :rows="7"
                              :save-indicator="false"
                          />
                        </v-col>
                        <v-col cols="12" sm="6" order="1" order-sm="2">
                          <v-row>
                            <v-col class="d-flex justify-content justify-center align-content-center" cols="5"
                                   style="flex-direction: column">
                              <v-img
                                  :src="laptop.href"
                                  max-height="30vh"
                                  :contain="true"
                                  :eager="prerendering"
                                  alt="An example image showing a drawing based on the description below."
                              />
                            </v-col>
                            <v-col cols="7">
                              <h2>Example description</h2>
                              Vulpy:<br/>
                              * is a fox<br/>
                              * is about three feet tall<br/>
                              * has orange fur, with white on his belly, cheeks, 'socks', and inner ears<br/>
                              * has a paintbrush tail that can be any color, but is black for this piece.<br/>
                              * has pink pawpads<br/><br/>
                              Please draw Vulpy sitting and typing away excitedly on a computer!
                            </v-col>
                          </v-row>
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="12" order="3">
                          <ac-bound-field
                              field-type="ac-uppy-file"
                              uppy-id="uppy-new-order"
                              :field="orderForm.fields.references"
                              :max-number-of-files="10"
                              label="(Optional) Add some reference images!"
                              :persistent-hint="true"
                              :persist="true"
                          />
                        </v-col>
                      </v-row>
                    </v-stepper-window-item>
                    <v-stepper-window-item :value="3">
                      <v-row v-if="invoicing">
                        <v-col cols="12">
                          <v-card>
                            <v-card-text>
                              <p><span class="title">When you hit 'Create Invoice'...</span></p>
                              <p>You will be brought to an order page, where you can then adjust terms/line items and
                                finalize once ready. Once finalized, the invoice will be sent to the customer
                                (if you provided a username or email).
                              </p>
                            </v-card-text>
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row v-else>
                        <v-col cols="12">
                          <v-alert type="warning" :value="true" v-if="product.x.wait_list">
                            This order will be waitlisted. Waitlisted orders are not guaranteed to be accepted on any
                            particular time table and may not be fulfilled in the order they are received. Please check
                            the
                            product description for further details or contact the artist if there is any confusion.
                            <strong>You will not be expected to pay for this order unless and until it is
                              accepted.</strong>
                          </v-alert>
                          <v-alert type="info" :value="true">
                            Once your order is placed, the artist will review your request, make any adjustments to the
                            quote as needed, and present them for your approval and payment. We will update you via
                            email as things progress.
                          </v-alert>
                        </v-col>
                        <v-col cols="12">
                          <ac-load-section :controller="subjectHandler.artistProfile">
                            <template v-slot:default>
                              <v-list-subheader v-if="subjectHandler.artistProfile.x!.commission_info">Commission Info
                              </v-list-subheader>
                              <ac-rendered :value="subjectHandler.artistProfile.x!.commission_info" :truncate="500"/>
                            </template>
                          </ac-load-section>
                        </v-col>
                        <v-col cols="12">
                          <v-alert type="info" :value="true">
                            All orders are bound by the
                            <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement.</router-link>
                          </v-alert>
                        </v-col>
                        <v-col cols="12" v-if="product.x.escrow_enabled || !product.x.escrow_upgradable">
                          <ac-escrow-label :escrow="product.x.escrow_enabled" name="product"/>
                        </v-col>
                        <template v-else>
                          <v-col cols="12" sm="6">
                            <ac-escrow-label :escrow="product.x.escrow_enabled" :upgrade-available="true"
                                             name="product"/>
                          </v-col>
                          <v-col cols="6">
                            <ac-bound-field
                                :field="orderForm.fields.escrow_upgrade" field-type="v-checkbox"
                                :label="shieldUpgradeLabel"
                            />
                          </v-col>
                        </template>
                      </v-row>
                    </v-stepper-window-item>
                  </v-stepper-window>
                </v-stepper>
                <v-card-actions row wrap>
                  <v-spacer></v-spacer>
                  <v-btn @click.prevent="orderForm.step -= 1" v-if="orderForm.step > 1" color="secondary"
                         class="previous-button" variant="flat">Previous
                  </v-btn>
                  <v-btn @click.prevent="orderForm.step += 1" v-if="orderForm.step < 3" color="primary"
                         class="next-button" variant="flat" :disabled="!!nextDisabled">Next
                  </v-btn>
                  <v-btn type="submit" v-if="orderForm.step === 3" color="primary" class="submit-button" variant="flat">
                    <span v-if="invoicing">
                      Create Invoice
                    </span>
                    <span v-else>
                      Agree and Place Order
                    </span>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </ac-form-container>
          </ac-form>
        </v-col>
        <v-col cols="12" offset-md="1" md="3" lg="2">
          <v-toolbar dense color="black">
            <ac-avatar :user="product.x.user" :show-name="false" class="ml-3"/>
            <v-toolbar-title class="ml-1">
              <ac-link :to="profileLink(product.x.user)">{{username}}</ac-link>
            </v-toolbar-title>
          </v-toolbar>
          <v-card :color="$vuetify.theme.current.colors['well-darken-2']">
            <v-card-text>
              <v-row dense>
                <v-col class="title" cols="12">
                  Order Summary
                </v-col>
                <v-col class="subheading" cols="12">
                  {{product.x.name}}
                </v-col>
                <v-col cols="12">
                  <ac-asset :asset="product.x.primary_submission" thumb-name="thumbnail" :aspect-ratio="1" :alt="productSubmissionText"/>
                </v-col>
                <v-col class="subtitle-1" cols="12" v-if="product.x.name_your_price">
                  Name your price!
                </v-col>
                <v-col class="subtitle-1" cols="12" v-else>
                  Starts at ${{currentPrice.toFixed(2)}}
                  <p v-if="shielded">
                    <small>(${{product.x.starting_price.toFixed(2)}} + ${{shieldCost.toFixed(2)}} shield fee)</small>
                  </p>
                </v-col>
                <v-col>
                  <span v-if="product.x.revisions">
                    <strong>{{product.x.revisions}}</strong> revision<span v-if="product.x.revisions > 1">s</span> included.
                  </span>
                </v-col>
                <v-col cols="12">
                  <span>Estimated completion: <strong>{{formatDateTerse(deliveryDate!)}}</strong></span>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {useProduct} from '@/components/views/product/mixins/ProductCentric.ts'
import AcAsset from '@/components/AcAsset.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import Order from '@/types/Order.ts'
import {User} from '@/store/profiles/types/User.ts'
import AcRendered from '@/components/wrappers/AcRendered.ts'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {artCall, BASE_URL, prepopulateCharacters} from '@/lib/lib.ts'
import {Character} from '@/store/characters/types/Character.ts'
import AcEscrowLabel from '@/components/AcEscrowLabel.vue'
import {useForm} from '@/store/forms/hooks.ts'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import ProductProps from '@/types/ProductProps.ts'
import {computed, onMounted, ref, watch} from 'vue'
import {useViewer} from '@/mixins/viewer.ts'
import {useRoute, useRouter} from 'vue-router'
import {useSubject} from '@/mixins/subjective.ts'
import {usePrerendering} from '@/mixins/prerendering.ts'
import {formatDateTerse} from '@/lib/otherFormatters.ts'
import {profileLink} from '@/lib/otherFormatters.ts'
import {RawData} from '@/store/forms/types/RawData.ts'
import debounce from 'lodash/debounce'
import {statusOk} from '@/mixins/ErrorHandling.ts'
import {ShoppingCart} from '@/types/ShoppingCart.ts'

declare interface NewOrderProps {
  invoiceMode?: string,
}

const props = defineProps<NewOrderProps & SubjectiveProps & ProductProps>()
const {product, deliveryDate} = useProduct(props)
const showCharacters = ref(false)
const initCharacters = ref<Character[]>([])
// Do we still need this? Or is there now a better way?
const clickCounter = ref(0)
const laptop = new URL('/static/images/laptop.png', BASE_URL)

const {viewer, viewerHandler, rawViewerName, isStaff, isRegistered, viewerName} = useViewer()
const {isCurrent, subjectHandler} = useSubject(props)


watch(viewer, () => {
  if (viewer && (viewer.value as User).guest_email) {
    const value = (viewer.value as User).guest_email
    orderForm.fields.email.update(value)
  }
})

// The way we're constructed allows us to avoid refetching if we arrive through the product page, but
// leaves us in the same scroll position as we were. Fix that here.
onMounted(() => window.scrollTo(0, 0))

const route = useRoute()
const router = useRouter()

const forceShield = computed(() => !!({...route.query}.forceShield))
const invoicing = computed(() => isCurrent.value || (isStaff.value && !!props.invoiceMode))

let step = parseInt(route.query.stepId + '') || 1
if (step > 3) {
  step = 3
} else if (step < 1) {
  step = 1
}

const validators = [{name: 'email'}]
if (props.invoiceMode) {
  validators.pop()
}

const cartDefaults: ShoppingCart = {
  product: parseInt(route.params.productId as string, 10),
  email: ((viewer.value as User).guest_email || ''),
  private: false,
  characters: [],
  rating: 0,
  details: '',
  references: [],
  named_price: null,
  escrow_upgrade: forceShield.value,
}

if (window.CART) {
  // Rehydrate the shopping cart.
  if (!cartDefaults.email) {
    cartDefaults.email = window.CART.email
  }
  cartDefaults.private = window.CART.private
  cartDefaults.characters = window.CART.characters
  cartDefaults.rating = window.CART.rating
  cartDefaults.details = window.CART.details
  cartDefaults.references = window.CART.references
  cartDefaults.named_price = window.CART.named_price
  cartDefaults.escrow_upgrade = window.CART.escrow_upgrade
}

const orderUrl = computed(() => `${product.endpoint}order/`)

const orderForm = useForm('newOrder', {
  endpoint: orderUrl.value,
  persistent: true,
  step,
  fields: {
    // product field not actually used in submission, but used as a way to track
    // whether the user is revisiting this product after navigating away, or if this is the first time.
    // We start with zero to make sure we register a 'change' on the first product visited and copy over the
    // details template from the product, if it exists.
    //
    // It is also used to track the order for the purposes of someone returning to this 'cart'. The data in this form
    // must be synchronizable to the data in backend/apps/sales/models.py, in the ShoppingCart model.
    product: {value: cartDefaults.product},
    email: {
      value: cartDefaults.email,
      step: 1,
      validators: validators,
    },
    private: {
      value: cartDefaults.private,
      step: 1,
    },
    characters: {
      value: cartDefaults.characters,
      step: 2,
    },
    rating: {
      value: cartDefaults.rating,
      step: 2,
    },
    details: {
      value: cartDefaults.details,
      step: 2,
    },
    references: {
      value: cartDefaults.references,
      step: 2,
    },
    invoicing: {
      value: false,
      step: 3,
    },
    named_price: {
      value: cartDefaults.named_price,
      step: 1,
    },
    // Note: There are agreements and warnings to display on step 3 even if there aren't fields,
    // so if this field gets moved to a lower step, a dummy field should be created for step 3 to persist.
    escrow_upgrade: {
      value: cartDefaults.escrow_upgrade,
      step: 3,
    },
  },
})

watch(orderUrl, (newURL) => {orderForm.endpoint = newURL}, {immediate: true})

orderForm.fields.invoicing.update(invoicing.value)

onMounted(() => orderForm.step = step)

// @ts-ignore
window.orderForm = orderForm



watch(() => product.x, (newProduct) => {
  if (!newProduct) {
    return
  }
  orderForm.fields.rating.model = Math.min(newProduct.max_rating, orderForm.fields.rating.value)
  if ((orderForm.fields.product.value !== newProduct.id) && newProduct.details_template.length) {
    orderForm.fields.details.model = newProduct.details_template
  }
  orderForm.fields.product.model = newProduct.id
}, {deep: true, immediate: true})

// Keep the order form's step as part of the URL.
watch(() => orderForm.step, (val: number) => {
  router.replace({
    query: {
      ...route.query,
      stepId: `${val}`,
    },
  })
}, {immediate: true})

const nextDisabled = computed(() => {
  // Touch the order form so this is re-evaluated whenever it changes.
  // Just checking the email field isn't enough since Vue can't listen for it.
  // eslint-disable-next-line no-unused-expressions
  clickCounter.value
  const element = document.querySelector('#field-newOrder__email')
  if (!element) {
    return false
  }
  return document.activeElement && document.activeElement.id === element.id
})

const goToOrder = (order: Order) => {
  // Could take a while. Let's not make it look like we're done.
  orderForm.sending = true
  const link = {...order.default_path}
  link.query = {
    ...link.query,
    showConfirm: 'true',
  }
  if (!isRegistered.value) {
    link.params!.username = rawViewerName.value
    viewerHandler.refresh().then(() => {
      router.push(link)
      orderForm.sending = false
    })
    return
  }
  // Special case override for table events.
  if ((product.x?.table_product && isStaff.value) || invoicing.value) { // eslint-disable-line camelcase
    link.query.view_as = 'Seller'
    link.name = 'SaleDeliverablePayment'
    delete link.query.showConfirm
  }
  if (!props.invoiceMode) {
    window.fbq('track', 'Purchase', {
      value: currentPrice.value,
      currency: 'USD',
      content_ids: [product.x!.id],
      content_name: product.x!.name,
    })
  }
  router.push(link)
  orderForm.sending = false
}

const submitAction = () => {
  if (orderForm.step < 3) {
    orderForm.step += 1
    return
  }
  orderForm.submitThen(goToOrder)
}

const shielded = computed(() => {
  if (!product.x) {
    return false
  }
  if (product.x.escrow_enabled) {
    return true
  }
  return (product.x.escrow_upgradable && orderForm.fields.escrow_upgrade.value)
})

const currentPrice = computed(() => {
  if (!product.x) {
    return NaN
  }
  if (shielded.value) {
    return product.x.shield_price
  }
  return product.x.starting_price
})


const shieldCost = computed(() => {
  if (!product.x) {
    return 0
  }
  return product.x.shield_price - product.x.starting_price
})

const shieldUpgradeLabel = computed(() => {
  if (!product.x) {
    return 'Add Shield Protection'
  }
  const text = 'Add Shield Protection for '
  return text + `$${shieldCost.value.toFixed(2)}`
})

const privateHint = computed(() => {
  if (invoicing.value) {
    return 'Mark if the client has requested that this piece be private-- which means that it will not be publicly ' +
        'shown, and copyright will be assigned to them by default (if applicable and legally possible, and your ' +
        'commission info in your artist settings does not explicitly say otherwise). You are advised to upcharge ' +
        'for this if you do it.'
  } else {
    return 'Hides the resulting submission from public view and tells the artist you want this commission ' +
        'to be private. The artist may charge an additional fee, since they will not be able to use the piece ' +
        'in their portfolio.'
  }
})

const productSubmissionText = computed(() => {
  if (product.x && product.x.primary_submission) {
    const title = product.x.primary_submission.title
    if (!title) {
      return `Untitled Focus Submission for ${product.x.name}`
    }
    return `Focus Submission for ${product.x.name} titled: ${title}`
  }
  return ''
})

const {prerendering} = usePrerendering()

const rawUpdateCart = (rawData: RawData) => {
  if (invoicing.value) {
    return
  }
  artCall({url: '/api/sales/cart/', method: 'patch', data: rawData}).catch(statusOk(400))
}

const updateCart = debounce(rawUpdateCart, 250, {trailing: true})

watch(() => orderForm.rawData, updateCart, {deep: true, immediate: true})

subjectHandler.artistProfile.get().then()
prepopulateCharacters(orderForm.fields.characters, showCharacters, initCharacters)
</script>
