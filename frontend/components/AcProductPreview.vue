<template>
  <v-sheet v-if="carousel" color="grey-darken-2" class="product-preview">
    <v-container fluid class="pa-0">
      <v-row
          class="fill-height"
          justify="center"
          align="center"
      >
        <v-col cols="12" sm="4">
          <v-row no-gutters align-content="center" justify="center">
            <v-col cols="6" sm="12" lg="8">
              <ac-link :to="{name: 'Product', params: {productId: `${product.id}`, username: product.user.username}}">
                <ac-hidden-flag :value="product.table_product || product.hidden"/>
                <ac-asset :asset="product.primary_submission" thumb-name="thumbnail" :aspect-ratio="1" :alt="productAltText" :eager="eager"/>
              </ac-link>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="12" md="5" align-self="center">
          <v-card>
            <v-card-text>
              <v-row class="fill-height" no-gutters>
                <v-col cols="12" class="text-center hidden-sm-and-down title py-3">
                  <ac-link :to="productLink" class="text-center">
                    {{product.name}}
                  </ac-link>
                </v-col>
                <v-col cols="12" class="text-center hidden-md-and-up">
                  <strong>
                    {{product.name}}
                  </strong>
                </v-col>
                <v-col cols="12" class="hidden-md-and-up">
                  <v-row no-gutters>
                    <v-col class="shrink" align-self="start">
                      <span v-if="product.name_your_price">Name your price!</span>
                      <span v-else>From ${{product.starting_price.toFixed(2)}}</span>
                    </v-col>
                    <v-spacer></v-spacer>
                    <v-col class="shrink" align-self="end">
                      <ac-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
                        <v-tooltip bottom v-if="product.escrow_enabled" aria-label="Tooltip for shield indicator">
                          <template v-slot:activator="{props}">
                            <v-icon color="green" class="pl-1" small v-bind="props" :icon="mdiShieldHalfFull" aria-label="Learn More About this product's shield protection."/>
                          </template>
                          <span>Protected by Artconomy Shield</span>
                        </v-tooltip>
                      </ac-link>
                    </v-col>
                  </v-row>
                </v-col>
                <v-col class="text-center hidden-sm-and-down" cols="12" v-if="product.escrow_enabled">
                  <ac-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
                    <v-icon color="green" class="pr-1" :icon="mdiShieldHalfFull"/>
                    <span>Protected by Artconomy Shield</span>
                  </ac-link>
                </v-col>
                <v-col cols="6" class="hidden-sm-and-down">
                  <v-row class="fill-height" align="center" justify="center" no-gutters>
                    <v-col cols="12" class="text-center no-underline">
                      <ac-link :to="productLink"><span class="days-turnaround">{{turnaround}}</span></ac-link>
                    </v-col>
                    <v-col cols="12" class="text-center">
                      <ac-link :to="productLink">days turnaround</ac-link>
                    </v-col>
                  </v-row>
                </v-col>
                <v-col cols="6" class="hidden-sm-and-down">
                  <v-col cols="12" class="pb-1 no-underline">
                    <ac-link :to="productLink" v-if="product.name_your_price">Name Your Price!</ac-link>
                    <ac-link :to="productLink" v-else>Starting at</ac-link>
                  </v-col>
                  <v-col cols="12" class="no-underline" v-if="!product.name_your_price">
                    <ac-link :to="productLink">
                      <span class="currency-notation" v-if="product.starting_price">$</span>
                      <span class="price-display">{{product.starting_price.toFixed(2)}}</span>
                    </ac-link>
                  </v-col>
                </v-col>
                <v-col cols="12" class="hidden-sm-and-down">
                  <v-toolbar color="black" density="compact">
                    <ac-avatar :user="product.user" :show-name="false" class="ml-1" />
                    <v-toolbar-title>{{product.user.username}}</v-toolbar-title>
                  </v-toolbar>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-sheet>
  <v-responsive v-else-if="$vuetify.display.smAndDown || mini" aspect-ratio="1" :class="{unavailable}"
                class="product-preview">
    <v-card>
      <v-container fluid class="pa-2">
        <v-row no-gutters class="pb-2">
          <v-col cols="8" offset="2">
            <ac-link :to="productLink">
              <ac-hidden-flag :value="product.table_product || product.hidden"/>
              <ac-asset :text="false" :asset="product.primary_submission" thumb-name="thumbnail" :aspect-ratio="1"
                        :allow-preview="false" :alt="productAltText"/>
            </ac-link>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="12">
            <ac-link :to="productLink">{{product.name}}</ac-link>
          </v-col>
          <v-col cols="12">
            <v-row no-gutters>
              <v-col class="grow" v-if="product.name_your_price"><small>Name Your Price!</small></v-col>
              <v-col class="grow" v-else><small>From</small> ${{product.starting_price.toFixed(2)}}</v-col>
              <v-col class="no-underline shrink">
                <ac-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
                  <v-tooltip bottom v-if="product.escrow_enabled || product.escrow_upgradable" aria-label="Tooltip for shield status indicator">
                    <template v-slot:activator="{props}">
                      <v-icon :color="shieldColor" class="pl-1" small v-bind="props" :icon="mdiShieldHalfFull"/>
                      <span class="d-sr-only">Learn more about shield.</span>
                    </template>
                    <span v-if="product.escrow_enabled || forceShield">Protected by Artconomy Shield</span>
                    <span v-else>Shield upgrade available for this product</span>
                  </v-tooltip>
                </ac-link>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-responsive>
  <v-card class="product-preview" :class="{unavailable}" v-else>
    <ac-link :to="productLink">
      <ac-hidden-flag :value="product.table_product || product.hidden"/>
      <ac-asset :asset="product.primary_submission" thumb-name="thumbnail" :aspect-ratio="1" :allow-preview="false" :alt="productAltText"/>
    </ac-link>
    <v-card-text class="pt-2">
      <v-row no-gutters>
        <v-col class="text-left">
          <ac-link :to="productLink">{{product.name}}</ac-link>
          <span v-if="showUsername">
            By
            <ac-link
                :to="{name: 'Products', params: {username: product.user.username}}">{{product.user.username}}</ac-link>
          </span>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col>
          <v-row no-gutters>
            <ac-link :to="{name: 'Ratings', params: {username: product.user.username}}" v-if="product.user.stars">
              <v-rating density="compact" size="small" half-increments :model-value="product.user.stars" color="primary"/>
            </ac-link>
            <v-spacer v-else/>
            <ac-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
              <v-tooltip bottom v-if="product.escrow_enabled || product.escrow_upgradable" aria-label="Shield Status Tooltip">
                <template v-slot:activator="{props}">
                  <v-icon :color="shieldColor" class="pl-1" v-bind="props" :icon="mdiShieldHalfFull" aria-label="Learn more about Shield."/>
                  <span class="d-sr-only">Learn more about shield.</span>
                </template>
                <span v-if="product.escrow_enabled || forceShield">Protected by Artconomy Shield</span>
                <span v-else>Shield upgrade available for this product</span>
              </v-tooltip>
            </ac-link>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters class="mt-2">
        <v-col class="shrink d-flex">
          <v-row no-gutters align-content="end" align="end">
            <v-col>
              <v-spacer/>
              <ac-link :to="productLink">
                <v-row no-gutters>
                  <v-col class="shrink">
                    <ac-link :to="productLink">
                      <span class="days-turnaround">{{turnaround}}</span> days turnaround
                    </ac-link>
                  </v-col>
                </v-row>
              </ac-link>
            </v-col>
          </v-row>
        </v-col>
        <v-spacer/>
        <v-col class="d-flex" v-if="product.name_your_price">
          <ac-link :to="productLink" v-if="product.name_your_price">
            <v-row no-gutters>
              <v-col cols="12" class="pb-1">
                Name Your Price!
              </v-col>
            </v-row>
          </ac-link>
        </v-col>
        <v-col class="shrink d-flex" v-else>
          <ac-link :to="productLink">
            <v-row no-gutters>
              <v-col cols="12" class="pb-1">
                Starting at
              </v-col>
              <v-col cols="12">
                <span class="currency-notation" v-if="product.starting_price">$</span>
                <span class="price-display">{{startingPrice}}</span>
              </v-col>
            </v-row>
          </ac-link>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.days-turnaround, .price-display {
  font-size: 2.5rem;
}

.unavailable {
  opacity: .5;
}
</style>

<style>
.product-preview a {
  text-decoration: none !important;
}
</style>

<script setup lang="ts">
import Product from '@/types/Product.ts'
import AcAsset from '@/components/AcAsset.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcHiddenFlag from '@/components/AcHiddenFlag.vue'
import {RouteLocationRaw} from 'vue-router'
import {mdiShieldHalfFull} from '@mdi/js'
import {computed} from 'vue'

declare interface AcProductPreviewProps {
  product: Product,
  mini?: boolean,
  carousel?: boolean,
  showUsername?: boolean,
  forceShield?: boolean,
  linked?: boolean,
  eager?: boolean,
}

const props = withDefaults(defineProps<AcProductPreviewProps>(), {
  mini: false,
  carousel: false,
  showUsername: true,
  forceShield: false,
  linked: true,
  eager: false,
})

const startingPrice = computed(() => {
  if (props.forceShield) {
    return props.product.shield_price.toFixed(2)
  }
  return props.product.starting_price.toFixed(2)
})

const shieldColor = computed(() => {
  if (props.forceShield) {
    return 'green'
  }
  if (props.product.escrow_enabled) {
    return 'green'
  }
  return ''
})

const productLink = computed(() => {
  if (!props.linked) {
    return undefined
  }
  const path: RouteLocationRaw = {
    name: 'Product',
    params: {
      username: props.product.user.username,
      productId: `${props.product.id}`,
    },
  }
  if (props.forceShield) {
    path.query = {forceShield: 'true'}
  }
  return path
})

const productAltText = computed(() => {
  if (!props.product.primary_submission) {
    return props.product.name
  }
  const title = props.product.primary_submission.title
  if (!title) {
    return `Untitled Showcase submission for ${props.product.name}`
  }
  return `Showcase submission for ${props.product.name} entitled `
})

const unavailable = computed(() => !props.product.available)

const turnaround = computed(() => Math.ceil(props.product.expected_turnaround))
</script>
