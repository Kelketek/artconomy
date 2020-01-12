<template>
  <ac-load-section :controller="pricing">
    <template v-slot:default>
      <v-row no-gutters   v-if="validPrice">
        <v-col class="text-right pr-1" cols="6" v-if="lineItems.length">Base Price:</v-col>
        <v-col class="text-left pl-1" cols="6" v-if="lineItems.length">${{basePrice.toFixed(2)}}</v-col>
        <template v-for="item in lineItems">
          <v-col class="text-right pr-1" cols="6" :key="'label-' + item.label">{{item.label}}:</v-col>
          <v-col class="text-left pl-1" align-self="center" cols="6" :key="'value-' + item.label">${{item.value.toFixed(2)}}</v-col>
        </template>
        <v-col class="text-right pr-1" cols="6" ><strong>Total Price:</strong></v-col>
        <v-col class="text-left pl-1" cols="6" >${{rawPrice.toFixed(2)}}</v-col>
        <v-col class="text-right pr-1" cols="6" v-if="escrow">Shield Protection (Included):</v-col>
        <v-col class="text-left pl-1" align-self="center" cols="6" v-if="escrow">$-{{serviceFee.toFixed(2)}}</v-col>
        <v-col class="text-right pr-1" cols="6" v-if="landscape && isSeller"><strong>Landscape Bonus:</strong></v-col>
        <v-col class="text-left pl-1" align-self="center" cols="6" v-if="landscape && isSeller"><strong>${{landscapeBonus.toFixed(2)}}</strong></v-col>
        <v-col class="text-right pr-1" cols="6" v-if="isSeller && escrow"><strong>Your Payout:</strong></v-col>
        <v-col class="text-left pl-1" align-self="center" cols="6" v-if="isSeller && escrow"><strong>${{payout.toFixed(2)}}</strong></v-col>
        <v-col class="text-center pt-2" cols="12" v-if="!landscape && isSeller && escrow" >
          You could earn <strong>${{landscapeBonus.toFixed(2)}}</strong> more with
          <router-link :to="{name: 'Upgrade'}">Artconomy Landscape</router-link>!
        </v-col>
      </v-row>
      <v-row no-gutters   v-else>
        <v-col class="text-center" v-if="(basePrice !== 0) && escrow">
          You must enter a price higher than ${{pricing.x.minimum_price.toFixed(2)}},
          if you plan to charge for this product.
        </v-col>
      </v-row>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Subjective from '../mixins/subjective'
import {Prop} from 'vue-property-decorator'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'
import Component, {mixins} from 'vue-class-component'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import LineItem from '@/types/LineItem'

function quantize(value: number) {
  return parseFloat(value.toFixed(2))
}

@Component({
  components: {AcLoadSection},
})
export default class AcPricePreview extends mixins(Subjective) {
    public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
    @Prop({required: true})
    public price!: string
    @Prop({required: false, default: () => []})
    public lineItems!: LineItem[]
    @Prop({default: true})
    public isSeller!: boolean
    @Prop({default: true})
    public escrow!: boolean

    public get basePrice() {
      return parseFloat(this.price)
    }

    public get adjustmentPrice() {
      const result = this.lineItems.reduce((previousValue: LineItem, nextValue: LineItem) => {
        return {label: 'adjustment', value: previousValue.value + nextValue.value}
      }, {label: 'adjustment', value: 0})
      return (result && result.value) || 0
    }

    public get rawPrice() {
      return quantize(this.basePrice + this.adjustmentPrice)
    }

    public get payout() {
      return quantize(this.rawPrice - this.serviceFee + this.userBonus)
    }

    public get userBonus() {
      if (this.landscape) {
        return this.landscapeBonus
      }
      return 0
    }

    public get landscape() {
      if (!this.escrow) {
        return false
      }
      /* istanbul ignore if */
      if (!this.subject) {
        return false
      }
      /* istanbul ignore if */
      if (!('landscape' in this.subject)) {
        return false
      }
      return this.subject.landscape
    }

    public get landscapeBonus() {
      if (!this.pricing.x) {
        return NaN
      }
      const pricing = this.pricing.x
      const base = pricing.standard_percentage * 0.01 * this.rawPrice
      return (base * 0.01 * pricing.premium_percentage_bonus) + pricing.premium_static_bonus
    }

    public get validPrice() {
      if (!this.pricing.x) {
        return false
      }
      return this.rawPrice >= this.pricing.x.minimum_price
    }

    public get serviceFee() {
      if (!this.pricing.x) {
        return NaN
      }
      if (!this.escrow) {
        return 0
      }
      const percentageMultiplier = this.pricing.x.standard_percentage * 0.01
      return quantize((this.rawPrice * percentageMultiplier) + this.pricing.x.standard_static)
    }
    public created() {
      this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/v1/pricing-info/'})
      this.pricing.get()
    }
}
</script>
