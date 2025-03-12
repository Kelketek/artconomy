<template>
  <v-autocomplete
    ref="input"
    v-model="tags"
    v-model:search="query"
    chips
    :multiple="multiple"
    autocomplete
    :items="items"
    hide-no-data
    auto-select-first
    deletable-chips
    hide-selected
    cache-items
    :filter="itemFilter"
    item-value="id"
    :item-title="formatName"
    v-bind="fieldAttrs"
  />
</template>

<script setup lang="ts">
import {
  autocompleteDefaults,
  AutocompleteEmits,
  AutocompleteProps,
  useAutocomplete,
} from "@/components/fields/mixins/autocomplete.ts"
import { ref, useAttrs } from "vue"
import { VAutocomplete } from "vuetify/lib/components/VAutocomplete/index.mjs"
import type { Product, SubjectiveProps } from "@/types/main"

const props = withDefaults(
  defineProps<AutocompleteProps & SubjectiveProps>(),
  autocompleteDefaults(),
)
const input = ref<null | typeof VAutocomplete>(null)
const fieldAttrs = useAttrs()
const emit = defineEmits<{ "update:modelValue": [AutocompleteEmits] }>()
const url = `/api/sales/search/product/${props.username}/`
const { tags, query, items, itemFilter, searchTags } = useAutocomplete({
  props,
  emit,
  input,
  endpoint: url,
})
if (props.immediateSearch) {
  searchTags(query.value || "")
}

const formatName = (item: Product | number | unknown[]) => {
  /* istanbul ignore if */
  if (Array.isArray(item)) {
    // Type mismatch thrown by parent library. Return an empty string for this.
    return ""
  }
  if (typeof item === "number") {
    // Don't have the definition, just the ID.
    return `Product #${item}`
  }
  return `${item.name} starting at $${item.starting_price}`
}
</script>
