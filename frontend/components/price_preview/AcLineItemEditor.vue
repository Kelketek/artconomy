<template>
  <v-row no-gutters>
    <v-col class="text-right pr-1" cols="4"><ac-patch-field :patcher="line.patchers.description" :placeholder="placeholder"/></v-col>
    <v-col class="text-left pl-1" cols="4"><ac-patch-field :patcher="line.patchers.amount" field-type="ac-price-field"/></v-col>
    <v-col class="text-left pl-1" cols="2"><v-text-field :disabled="true" :value="'$' + price.toFixed(2)" /></v-col>
    <v-col cols="2" align-self="center" class="text-center">
      <v-btn x-small fab color="red" @click.prevent="line.delete" v-if="deletable">
        <v-icon>delete</v-icon>
      </v-btn>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import Vue from 'vue'
import {Prop} from 'vue-property-decorator'
import LineItem from '@/types/LineItem'
import Component from 'vue-class-component'
import LineAccumulator from '@/types/LineAccumulator'
import {SingleController} from '@/store/singles/controller'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import Big from 'big.js'
import {LineTypes} from '@/types/LineTypes'
@Component({
  components: {AcPatchField},
})
export default class AcLineItemEditor extends Vue {
  @Prop({required: true})
  public line!: SingleController<LineItem>
  @Prop({required: true})
  public priceData!: LineAccumulator

  public get deletable() {
    return (this.line.x as LineItem).type !== LineTypes.BASE_PRICE
  }

  public get price() {
    return this.priceData.map.get(this.line.x as LineItem) as Big
  }

  public get placeholder() {
    if ((this.line.x as LineItem).type === 0) {
      return 'Base price'
    }
    if ((this.line.x as LineItem).type === 1) {
      if (this.price.lt(0)) {
        return 'Discount'
      } else {
        return 'Additional requirements'
      }
    }
    const BASIC_TYPES: {[key: number]: string} = {
      0: 'Base price',
      2: 'Shield protection',
      3: 'Landscape bonus',
      4: 'Tip',
      5: 'Table service',
      6: 'Tax',
      7: 'Accessory item',
    }
    return BASIC_TYPES[(this.line.x as LineItem).type] || 'Other'
  }
}
</script>
