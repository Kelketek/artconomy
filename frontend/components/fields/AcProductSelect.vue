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

<script setup lang="ts">
import {
  autocompleteDefaults,
  AutocompleteEmits,
  AutocompleteProps, useAutocomplete,
} from '@/components/fields/mixins/autocomplete.ts'
import Product from '@/types/Product.ts'
import {ref, useAttrs} from 'vue'
import {VAutocomplete} from 'vuetify/lib/components/VAutocomplete/index.mjs'
import SubjectiveProps from '@/types/SubjectiveProps.ts'

const props = withDefaults(defineProps<AutocompleteProps & SubjectiveProps>(), autocompleteDefaults())
const input = ref<null|typeof VAutocomplete>(null)
const fieldAttrs = useAttrs()
const emit = defineEmits<{'update:modelValue': [AutocompleteEmits]}>()
const url = `/api/sales/search/product/${props.username}/`
const {tags, query, items, itemFilter} = useAutocomplete(props, emit, input, url)

const formatName = (item: Product|number|unknown[]) => {
  /* istanbul ignore if */
  if (Array.isArray(item)) {
    // Type mismatch thrown by parent library. Return an empty string for this.
    return ''
  }
  if (typeof(item) === 'number') {
    // Don't have the definition, just the ID.
    return `Product #${item}`
  }
  return `${item.name} starting at $${item.starting_price}`
}
</script>
