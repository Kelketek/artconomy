<template>
  <v-autocomplete
      chips
      :multiple="multiple"
      v-model="tags"
      autocomplete
      v-model:search-input="query"
      :items="items"
      hide-no-data
      auto-select-first
      deletable-chips
      hide-selected
      cache-items
      :filter="itemFilter"
      item-value="id"
      :item-text="formatName"
      ref="input"
      v-bind="fieldAttrs"
  />
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import AcAvatar from '@/components/AcAvatar.vue'
import Autocomplete from '@/components/fields/mixins/autocomplete'
import Product from '@/types/Product'
import Subjective from '@/mixins/subjective'

@Component({
  components: {AcAvatar},
})
class AcProductSelect extends mixins(Autocomplete, Subjective) {
  public url = '/api/sales/search/product/mine/'

  public formatName(item: Product) {
    /* istanbul ignore if */
    if (Array.isArray(item)) {
      // Type mismatch thrown by parent library. Return an empty string for this.
      return ''
    }
    return `${item.name} starting at $${item.starting_price.toFixed(2)}`
  }

  public created() {
    this.url = `/api/sales/search/product/${this.username}/`
  }
}

export default toNative(AcProductSelect)
</script>
