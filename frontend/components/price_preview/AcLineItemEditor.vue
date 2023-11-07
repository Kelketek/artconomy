<template>
  <v-row no-gutters>
    <v-col class="text-right" cols="12">
      <ac-patch-field
          :patcher="line.patchers.description"
          :id="`lineItem-${line.x!.id}-description`"
          :disabled="disabled"
          density="compact"
          :placeholder="placeholder"
      />
    </v-col>
    <v-col class="text-left" cols="6">
      <ac-patch-field
          :patcher="line.patchers.amount"
          :id="`lineItem-${line.x!.id}-amount`"
          field-type="ac-price-field"
          :disabled="disabled"
          density="compact"
          @keydown.enter="newLineFunc"
      />
    </v-col>
    <v-col class="text-left" cols="4" md="5">
      <v-text-field :disabled="true" :value="'$' + price.toFixed(2)" density="compact"/>
    </v-col>
    <v-col cols="2" sm="1" class="text-center d-flex justify-center pl-1">
      <v-btn size="x-small" icon color="red" @click.prevent="line.delete" v-if="deletable" :disabled="disabled" class="align-self-start mt-1">
        <v-icon icon="mdi-delete"/>
      </v-btn>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import LineItem from '@/types/LineItem'
import LineAccumulator from '@/types/LineAccumulator'
import {SingleController} from '@/store/singles/controller'
import {Decimal} from 'decimal.js'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {LineTypes} from '@/types/LineTypes'

@Component({
  components: {AcPatchField},
  emits: ['new-line'],
})
class AcLineItemEditor extends Vue {
  @Prop({required: true})
  public line!: SingleController<LineItem>

  @Prop({required: true})
  public priceData!: LineAccumulator

  @Prop({default: false})
  public enableNewLine!: boolean

  @Prop({default: false})
  public disabled!: boolean

  public get deletable() {
    return (this.line.x as LineItem).type !== LineTypes.BASE_PRICE
  }

  public get price() {
    return this.priceData.subtotals.get(this.line.x as LineItem) as Decimal
  }

  public newLineFunc() {
    if (this.enableNewLine) {
      this.$emit('new-line')
    }
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
    const BASIC_TYPES: { [key: number]: string } = {
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

export default toNative(AcLineItemEditor)
</script>
