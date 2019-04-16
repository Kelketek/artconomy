<template>
<v-flex>
  <v-autocomplete
    chips
    :multiple="multiple"
    v-model="tags"
    autocomplete
    v-bind:search-input.sync="query"
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
>
</v-autocomplete>
</v-flex>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcAvatar from '@/components/AcAvatar.vue'
import Viewer from '@/mixins/viewer'
import Autocomplete from '@/components/fields/mixins/autocomplete'
import Product from '@/types/Product'
@Component({
  components: {AcAvatar},
})
export default class AcProductSelect extends mixins(Autocomplete, Viewer) {
  public url = `/api/sales/v1/search/product/mine/`
  public formatName(item: Product) {
    /* istanbul ignore if */
    if (Array.isArray(item)) {
      // Type mismatch thrown by parent library. Return an empty string for this.
      return ''
    }
    return `${item.name} starting at $${item.price.toFixed(2)}`
  }
}
</script>
