<template>
  <ac-load-section :controller="pricing">
    <template v-slot:default>
      <v-layout row wrap v-if="validPrice">
        <v-flex xs6 text-xs-right pr-1 v-if="adjustmentPrice">Base Price:</v-flex>
        <v-flex xs6 text-xs-left pl-1 v-if="adjustmentPrice">${{basePrice.toFixed(2)}}</v-flex>
        <v-flex xs6 text-xs-right pr-1 v-if="adjustmentPrice > 0">Additional Requirements:</v-flex>
        <v-flex xs6 text-xs-right pr-1 v-if="adjustmentPrice < 0">Discount:</v-flex>
        <v-flex xs6 text-xs-left pl-1 v-if="adjustmentPrice">${{adjustmentPrice.toFixed(2)}}</v-flex>
        <v-flex xs6 text-xs-right pr-1><strong>Total Price:</strong></v-flex>
        <v-flex xs6 text-xs-left pl-1>${{rawPrice.toFixed(2)}}</v-flex>
        <v-flex xs6 text-xs-right pr-1 v-if="escrow"><span v-if="!isSeller">(Included) </span>Artconomy Service Fee:</v-flex>
        <v-flex xs6 text-xs-left pl-1 v-if="escrow">$-{{serviceFee.toFixed(2)}}</v-flex>
        <v-flex xs6 text-xs-right pr-1 v-if="landscape && isSeller"><strong>Landscape Bonus:</strong></v-flex>
        <v-flex xs6 text-xs-left pl-1 v-if="landscape && isSeller"><strong>${{landscapeBonus.toFixed(2)}}</strong></v-flex>
        <v-flex xs6 text-xs-right pr-1 v-if="isSeller && escrow"><strong>Your Payout:</strong></v-flex>
        <v-flex xs6 text-xs-left pl-1 v-if="isSeller && escrow"><strong>${{payout.toFixed(2)}}</strong></v-flex>
        <v-flex xs12 v-if="!landscape && isSeller && escrow" text-xs-center pt-2>
          You could earn <strong>${{landscapeBonus.toFixed(2)}}</strong> more with
          <router-link :to="{name: 'Upgrade'}">Artconomy Landscape</router-link>!
        </v-flex>
      </v-layout>
      <v-layout row wrap v-else>
        <v-flex text-xs-center v-if="(basePrice !== 0) && escrow">
          You must enter a price higher than ${{pricing.x.minimum_price.toFixed(2)}},
          if you plan to charge for this product.
        </v-flex>
      </v-layout>
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
@Component({
  components: {AcLoadSection},
})
export default class AcPricePreview extends mixins(Subjective) {
    public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
    @Prop({required: true})
    public price!: string
    @Prop({default: '0.00'})
    public adjustment!: string
    @Prop({default: true})
    public isSeller!: boolean
    @Prop({default: true})
    public escrow!: boolean

    public get basePrice() {
      return parseFloat(this.price)
    }

    public get adjustmentPrice() {
      return parseFloat(this.adjustment)
    }

    public get rawPrice() {
      return this.basePrice + this.adjustmentPrice
    }

    public get payout() {
      return (this.rawPrice - this.serviceFee + this.userBonus)
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
      return ((this.rawPrice * percentageMultiplier) + this.pricing.x.standard_static)
    }
    public created() {
      this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/v1/pricing-info/'})
      this.pricing.get()
    }
}
</script>
