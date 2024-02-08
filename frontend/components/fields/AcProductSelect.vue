<template>
  <v-autocomplete
      chips
      :multiple="multiple"
      v-model="tags"
      autocomplete
      v-model:search="query"
      :items="items"
      hide-no-data
      auto-select-first
      deletable-chips
      hide-selected
      cache-items
      :filter="itemFilter"
      item-value="id"
      :item-title="formatName"
      ref="input"
      v-bind="fieldAttrs"
  />
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import AcAvatar from '@/components/AcAvatar.vue'
import Autocomplete from '@/components/fields/mixins/autocomplete.ts'
import Product from '@/types/Product.ts'
import Subjective from '@/mixins/subjective.ts'

@Component({
  components: {AcAvatar},
})
class AcProductSelect extends mixins(Autocomplete, Subjective) {
  public url = '/api/sales/search/product/mine/'

  public formatName(item: Product|number|unknown[]) {
    /* istanbul ignore if */
    if (Array.isArray(item)) {
      // Type mismatch thrown by parent library. Return an empty string for this.
      return ''
    }
    if (typeof(item) === 'number') {
      // Don't have the definition, just the ID.
      return `Product #${item}`
    }
    return `${item.name} starting at $${item.starting_price.toFixed(2)}`
  }

  public created() {
    this.url = `/api/sales/search/product/${this.username}/`
  }
}

export default toNative(AcProductSelect)
</script>
