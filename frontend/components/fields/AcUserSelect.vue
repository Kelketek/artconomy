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
    :item-value="itemValue"
    :allow-raw="allowRaw"
    item-title="username"
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
const {tags, query, items, itemFilter} = useAutocomplete({ props, emit, input, endpoint: '/api/profiles/search/user/', itemValue: props.itemValue })
</script>
