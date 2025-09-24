<template>
  <ac-form-dialog
    :model-value="modelValue"
    :large="true"
    :fluid="true"
    title="New Product"
    v-bind="newProduct.bind"
    @update:model-value="toggle"
    @submit.prevent="newProduct.submitThen(goToProduct)"
  >
    <template #top-buttons />
    <ac-load-section :controller="subjectHandler.artistProfile">
      <template #default>
        <v-col>
          <v-row
            v-if="subjectHandler.artistProfile.x!.bank_account_status === 0"
            no-gutters
          >
            <v-col class="pt-2" cols="12" md="8" offset-md="2">
              <ac-patch-field
                :patcher="
                  subjectHandler.artistProfile.patchers.bank_account_status
                "
                field-type="ac-bank-toggle"
                :username="username"
              />
            </v-col>
          </v-row>
          <v-stepper
            v-else
            v-model="newProduct.step"
            class="submission-stepper"
          >
            <v-stepper-header>
              <v-stepper-item
                :complete="newProduct.steps[1].complete"
                :value="1"
                :rules="newProduct.steps[1].rules"
                @click="newProduct.step = 1"
              >
                Basics
              </v-stepper-item>
              <v-divider />
              <v-stepper-item
                :complete="newProduct.steps[2].complete"
                :value="2"
                :rules="newProduct.steps[2].rules"
                @click="newProduct.step = 2"
              >
                Terms
              </v-stepper-item>
              <v-divider />
              <v-stepper-item
                :value="3"
                :rules="newProduct.steps[3].rules"
                @click="newProduct.step = 3"
              >
                Workload
              </v-stepper-item>
            </v-stepper-header>
            <v-stepper-window>
              <v-stepper-window-item :value="1">
                <v-row>
                  <v-col cols="12" sm="6" order="1" order-sm="1">
                    <ac-bound-field
                      :field="newProduct.fields.name"
                      label="Product Name"
                      hint="Pick a helpful name to describe what you're selling, such as 'Reference Sheet' or 'Line Drawing'."
                    />
                  </v-col>
                  <v-col cols="12" sm="6" order="3" order-sm="2">
                    <ac-bound-field
                      :field="newProduct.fields.hidden"
                      label="Hide Product"
                      field-type="ac-checkbox"
                      :persistent-hint="true"
                      hint="This product will not be immediately available. You will need to unhide the product in order for customers to order."
                    />
                  </v-col>
                  <v-col cols="12" order="2" order-sm="3">
                    <ac-bound-field
                      :field="newProduct.fields.tags"
                      label="Tags"
                      field-type="ac-tag-field"
                      hint="Add some tags to make it easy to search for your product."
                    />
                  </v-col>
                  <v-col cols="12" order="4" order-sm="4">
                    <ac-bound-field
                      :field="newProduct.fields.description"
                      label="Description"
                      field-type="ac-editor"
                      :save-indicator="false"
                      hint="Describe what you are offering. Remember that if you have general commission terms of service, you
                    can add these in your artist settings, and they will show on every product, so just include a
                    description of the product itself here."
                    />
                  </v-col>
                  <v-col cols="12" order="5" order-sm="5">
                    <v-expansion-panels>
                      <v-expansion-panel>
                        <v-expansion-panel-title
                          >Details Template</v-expansion-panel-title
                        >
                        <v-expansion-panel-text>
                          <v-row>
                            <v-col cols="6">
                              Optional. You may include a template for the
                              commissioner to fill out. You might do this if you
                              need to collect specific details for this
                              commission and want to avoid a lot of back and
                              forth. Here's an example template you might use:
                            </v-col>
                            <v-col cols="6">
                              <blockquote>
                                Preferred colors:<br /><br />
                                Do you want shading? (yes/no):<br /><br />
                                What are your social media accounts you'd like
                                me to tag when the piece is done?:
                              </blockquote>
                            </v-col>
                            <v-col cols="12">
                              <ac-bound-field
                                :field="newProduct.fields.details_template"
                                label="Details Template"
                                field-type="ac-editor"
                                :save-indicator="false"
                                :persistent-hint="true"
                              />
                            </v-col>
                          </v-row>
                        </v-expansion-panel-text>
                      </v-expansion-panel>
                    </v-expansion-panels>
                  </v-col>
                </v-row>
              </v-stepper-window-item>
              <v-stepper-window-item :value="2">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-row>
                      <v-col cols="12">
                        <v-row>
                          <v-col cols="12" md="6">
                            <v-checkbox
                              v-model="saleMode"
                              label="Sale mode"
                              hint="Check this to mark the item as on sale."
                            />
                          </v-col>
                          <v-col cols="12" md="6">
                            <ac-bound-field
                              :field="newProduct.fields.compare_at_price"
                              label="Compare at price"
                              field-type="ac-price-field"
                              :persistent-hint="true"
                              :disabled="!saleMode"
                              hint="The price the sale price is compared to."
                            />
                          </v-col>
                        </v-row>
                      </v-col>
                      <v-col cols="12" sm="6" lg="12">
                        <ac-bound-field
                          :field="newProduct.fields.base_price"
                          label="Take home amount"
                          field-type="ac-price-field"
                          :hint="priceHint"
                        />
                      </v-col>
                      <v-col cols="12" sm="6">
                        <ac-bound-field
                          :field="newProduct.fields.name_your_price"
                          field-type="v-switch"
                          label="Name Your Price"
                          :persistent-hint="true"
                          hint="If turned on, the base price is treated as a minimum price to cover costs,
                                     and the client is prompted to put in their own price. This is useful for 'Pay
                                     What You Want' commissions. You should note whatever impact the price has on the
                                     commission in the product details in order to avoid any dispute issues."
                          :true-value="true"
                          :false-value="false"
                          color="primary"
                        />
                      </v-col>
                      <v-col
                        v-if="(subject as User)!.paypal_configured"
                        cols="12"
                        sm="6"
                      >
                        <ac-bound-field
                          :field="newProduct.fields.paypal"
                          field-type="v-switch"
                          color="primary"
                          label="PayPal Invoicing"
                          :persistent-hint="true"
                          hint="If the order is marked unshielded, generate a PayPal invoice upon acceptance."
                          :true-value="true"
                          :false-value="false"
                        />
                      </v-col>
                      <v-col v-if="escrow" cols="12" sm="6">
                        <ac-bound-field
                          :field="newProduct.fields.escrow_enabled"
                          field-type="v-switch"
                          label="Shield enabled"
                          :persistent-hint="true"
                          hint="Enable shield protection for this product."
                          :true-value="true"
                          :false-value="false"
                          color="primary"
                        />
                      </v-col>
                      <v-col v-if="escrow" cols="12" sm="6">
                        <ac-bound-field
                          :field="newProduct.fields.escrow_upgradable"
                          field-type="v-switch"
                          label="Allow Shield Upgrade"
                          :persistent-hint="true"
                          :disabled="newProduct.fields.escrow_enabled.value"
                          :false-value="false"
                          :true-value="true"
                          color="primary"
                          hint="Allow user to upgrade to shield at their option, rather than requiring it. When upgrading, fee absorption is always off."
                        />
                      </v-col>
                    </v-row>
                  </v-col>
                  <v-col cols="12" md="6">
                    <ac-price-comparison
                      :username="username"
                      :line-item-set-maps="lineItemSetMaps"
                    />
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" sm="6">
                    <ac-bound-field
                      :field="newProduct.fields.expected_turnaround"
                      number
                      label="Expected Days Turnaround"
                      hint="How many standard business days you expect this task to take (on average)."
                      :persistent-hint="true"
                    />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <ac-bound-field
                      :field="newProduct.fields.revisions"
                      number
                      label="Included Revisions"
                      hint="How many revisions you're offering with this product. This does not include final
                                      delivery-- only intermediate WIP steps."
                      :persistent-hint="true"
                    />
                  </v-col>
                  <v-col cols="12">
                    <ac-bound-field
                      :field="newProduct.fields.max_rating"
                      label="Maximum Content Ratings"
                      field-type="ac-rating-field"
                    />
                  </v-col>
                </v-row>
              </v-stepper-window-item>
              <v-stepper-window-item :value="3">
                <v-row>
                  <v-col cols="12">
                    <h2>AWOO Workload Settings</h2>
                    <v-divider />
                    <p>
                      You can set these settings to help the Artconomy Workload
                      Organization and Overview tool manage your workload for
                      you.
                    </p>
                    <p>
                      <strong
                        >If you're not sure what to do here, or would like to
                        set these settings later, the defaults should be
                        safe.</strong
                      >
                    </p>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <ac-bound-field
                      :field="newProduct.fields.task_weight"
                      number
                      label="Workload Points"
                      hint="How many slots an order of this product should take up. If this task is
                                        particularly big, you may want it to take up more than one slot."
                      :persistent-hint="true"
                    />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <ac-bound-field
                      :field="newProduct.fields.wait_list"
                      label="Wait List Product"
                      field-type="ac-checkbox"
                      :disabled="!subject!.landscape"
                      hint="Marks this product as a waitlist product. Orders will be put in your
                                        waitlist queue which is separate from your normal order queue. You should specify
                                        your waitlist policy in the product description or in your commission info.
                                        This setting takes precedence over all other workload settings."
                      :persistent-hint="true"
                    />
                    <div v-if="!subject!.landscape">
                      This feature only available for
                      <router-link :to="{ name: 'Upgrade' }">
                        Landscape
                      </router-link>
                      subscribers.
                    </div>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-checkbox
                      v-model="limitAtOnce"
                      :persistent-hint="true"
                      label="Limit Availability"
                      hint="If you would like to make sure you're never doing more than a few of these at a time, check this box."
                    />
                  </v-col>
                  <v-col v-if="limitAtOnce" cols="12" sm="6">
                    <ac-bound-field
                      :persistent-hint="true"
                      :field="newProduct.fields.max_parallel"
                      type="number"
                      label="Maximum at Once"
                      min="1"
                      hint="If you already have this many orders of this product, don't allow customers to order any more."
                    />
                  </v-col>
                </v-row>
              </v-stepper-window-item>
            </v-stepper-window>
          </v-stepper>
        </v-col>
      </template>
    </ac-load-section>
    <template #bottom-buttons>
      <v-card-actions
        v-if="
          subjectHandler.artistProfile.x &&
          subjectHandler.artistProfile.x.bank_account_status !== 0
        "
        row
        wrap
      >
        <v-spacer />
        <v-btn variant="flat" @click.prevent="toggle(false)"> Cancel </v-btn>
        <v-btn
          v-if="newProduct.step > 1"
          color="secondary"
          variant="flat"
          @click.prevent="newProduct.step -= 1"
        >
          Previous
        </v-btn>
        <v-btn
          v-if="newProduct.step < 3"
          color="primary"
          variant="flat"
          @click.prevent="newProduct.step += 1"
        >
          Next
        </v-btn>
        <v-btn
          v-if="newProduct.step === 3"
          type="submit"
          color="primary"
          class="submit-button"
          :disabled="newProduct.sending"
          variant="flat"
        >
          Submit
        </v-btn>
      </v-card-actions>
      <v-card-actions v-else>
        <v-spacer />
        <v-btn @click.prevent="toggle(false)"> Cancel </v-btn>
      </v-card-actions>
    </template>
  </ac-form-dialog>
</template>
<script setup lang="ts">
import AcFormDialog from "@/components/wrappers/AcFormDialog.vue"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import AcBoundField from "@/components/fields/AcBoundField.ts"
import { useSubject } from "@/mixins/subjective.ts"
import { flatten, min } from "@/lib/lib.ts"
import { Ratings } from "@/types/enums/Ratings.ts"
import { deliverableLines, getTotals } from "@/lib/lineItemFunctions.ts"
import AcPriceComparison from "@/components/price_preview/AcPriceComparison.vue"
import { useErrorHandling } from "@/mixins/ErrorHandling.ts"
import { useSingle } from "@/store/singles/hooks.ts"
import { useForm } from "@/store/forms/hooks.ts"
import { computed, watch } from "vue"
import { useRouter } from "vue-router"
import { useList } from "@/store/lists/hooks.ts"
import { ListController } from "@/store/lists/controller.ts"
import type {
  LineItem,
  Pricing,
  Product,
  RawLineItemSetMap,
  SubjectiveProps,
} from "@/types/main"
import { User } from "@/store/profiles/types/main"

const props = defineProps<{ modelValue: boolean } & SubjectiveProps>()
const emit = defineEmits<{ "update:modelValue": [boolean] }>()
const router = useRouter()
const { subjectHandler, subject } = useSubject({ props })
const { setError } = useErrorHandling()

subjectHandler.artistProfile.get().catch(setError)
const pricing = useSingle<Pricing>("pricing", {
  endpoint: "/api/sales/pricing-info/",
})
pricing.get()

const url = computed(() => `/api/sales/account/${props.username}/products/`)
const newProduct = useForm(`${flatten(props.username)}__newProduct`, {
  endpoint: url.value,
  fields: {
    name: { value: "" },
    description: { value: "" },
    details_template: { value: "" },
    compare_at_price: {
      value: null,
      step: 2,
    },
    base_price: {
      value: "25.00",
      step: 2,
      validators: [{ name: "numeric" }],
    },
    expected_turnaround: {
      value: 5,
      step: 2,
      validators: [{ name: "numeric" }],
    },
    max_rating: {
      value: Ratings.GENERAL,
      step: 2,
    },
    wait_list: { value: false },
    task_weight: {
      value: 1,
      step: 3,
    },
    revisions: {
      value: 1,
      step: 2,
    },
    max_parallel: {
      value: 0,
      step: 3,
    },
    hidden: { value: false },
    table_product: { value: false },
    tags: { value: [] },
    escrow_enabled: {
      value: true,
      step: 2,
    },
    escrow_upgradable: {
      value: false,
      step: 2,
    },
    paypal: {
      value: true,
      step: 2,
    },
    name_your_price: {
      value: false,
      step: 2,
    },
  },
})

const startingAt = computed(() => {
  return (
    min(
      lineItemSetMaps.value.map((lineItemSetMap) =>
        parseFloat(
          getTotals(lineItemSetMap.lineItems.list.map((entry) => entry.x!))
            .total,
        ),
      ),
    ) || 0
  )
})

const saleMode = computed({
  get: () => {
    return !!newProduct.fields.compare_at_price.model
  },
  set: (value) => {
    if (!value) {
      newProduct.fields.compare_at_price.model = null
      return
    }
    if (newProduct.fields.compare_at_price.model) {
      return
    }
    newProduct.fields.compare_at_price.model = startingAt.value.toFixed(2)
  },
})

const escrow = computed(() => {
  const profile = subjectHandler.artistProfile.x
  return profile && profile.bank_account_status === 1
})

const goToProduct = (product: Product) => {
  router.push({
    name: "Product",
    params: {
      username: props.username,
      productId: product.id + "",
    },
    query: { editing: "true" },
  })
}

const limitAtOnce = computed({
  get: () => newProduct.fields.max_parallel.value !== 0,
  set: (value: boolean) => {
    const field = newProduct.fields.max_parallel
    if (value) {
      field.update(field.value || 1)
    } else {
      field.update(0)
    }
  },
})

const listControllerMaps = new Map(
  ["Shielded", "Unshielded", "__preferred"].map((name) => [
    name,
    useList<LineItem>(`newProduct${name}`, { endpoint: "#", paginated: false }),
  ]),
)

const rawLineItemSetMaps = computed((): RawLineItemSetMap[] => {
  if (!pricing.x) {
    return []
  }
  const sets = []
  const basePrice = newProduct.fields.base_price.value

  const planName = subject.value?.service_plan
  const international = !!subject.value?.international
  const tableProduct = newProduct.fields.table_product.value
  let preferredLines: LineItem[] = []
  let appendPreferred = false
  const options = {
    basePrice,
    international,
    pricing: pricing.x,
    escrowEnabled: true,
    tableProduct,
    extraLines: [],
  }
  if (
    escrow.value &&
    (newProduct.fields.escrow_enabled.value ||
      newProduct.fields.escrow_upgradable.value)
  ) {
    const escrowLines = deliverableLines({
      ...options,
      planName,
    })
    sets.push({
      name: "Shielded",
      lineItems: escrowLines,
      offer: false,
    })
    if (pricing && planName !== pricing.x.preferred_plan) {
      preferredLines = deliverableLines({
        ...options,
        planName: pricing.x.preferred_plan,
      })
      appendPreferred = true
    }
  }
  if (!escrow.value || !newProduct.fields.escrow_enabled.value) {
    const nonEscrowLines = deliverableLines({
      basePrice,
      international,
      planName,
      pricing: pricing.x,
      escrowEnabled: false,
      tableProduct,
      extraLines: [],
    })
    sets.push({
      name: "Unshielded",
      lineItems: nonEscrowLines,
      offer: false,
    })
  }
  if (appendPreferred) {
    sets.push({
      name: pricing.x?.preferred_plan + "",
      lineItems: preferredLines,
      offer: true,
    })
  }
  console.log(sets)
  return sets
})

const lineItemSetMaps = computed(() => {
  const sets = []
  for (const set of rawLineItemSetMaps.value) {
    const name = listControllerMaps.has(set.name) ? set.name : "__preferred"
    const controller = listControllerMaps.get(name) as ListController<LineItem>
    sets.push({ name: set.name, lineItems: controller, offer: set.offer })
  }
  return sets
})

watch(
  rawLineItemSetMaps,
  (rawLineItemSetMaps: RawLineItemSetMap[]) => {
    for (const set of rawLineItemSetMaps) {
      const name = listControllerMaps.has(set.name) ? set.name : "__preferred"
      const controller = listControllerMaps.get(
        name,
      ) as ListController<LineItem>
      controller.makeReady(set.lineItems)
    }
  },
  { deep: true, immediate: true },
)

const toggle = (value: boolean) => {
  emit("update:modelValue", value)
}

const priceHint = computed(() => {
  if (escrow.value) {
    return `Enter the listing price you want to present to the user. We will calculate what
                their fees will be for you. Adjust this number until you're happy with your cut and
                the total price. You will be able to adjust this
                price per-order if the client has special requests.`
  }
  return `Enter the listing price you want to present to the user. You will be able to adjust this
              price per-order if the client has special requests.`
})
</script>
