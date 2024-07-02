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
      :item-value="itemValue"
      :allow-raw="allowRaw"
      item-title="username"
      ref="input"
      v-bind="fieldAttrs"
  />
</template>

<script setup lang="ts">
import {
  autocompleteDefaults,
  AutocompleteEmits,
  AutocompleteProps,
  useAutocomplete,
} from '@/components/fields/mixins/autocomplete.ts'
import {ref, useAttrs} from 'vue'
import {VAutocomplete} from 'vuetify/lib/components/VAutocomplete/index.mjs'

const props = withDefaults(defineProps<{itemValue?: string} & AutocompleteProps>(), {...autocompleteDefaults(), itemValue: 'id'})
const input = ref<null|typeof VAutocomplete>(null)
const fieldAttrs = useAttrs()
const emit = defineEmits<{'update:modelValue': [AutocompleteEmits]}>()
const {tags, query, items, itemFilter} = useAutocomplete(props, emit, input, '/api/profiles/search/user/', props.itemValue)
</script>
