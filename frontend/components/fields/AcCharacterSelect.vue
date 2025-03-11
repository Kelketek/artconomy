<template>
  <v-autocomplete
    ref="input"
    v-model="tags"
    v-model:search="query"
    :chips="true"
    :multiple="multiple"
    autocomplete
    :items="items"
    :hide-no-data="true"
    :auto-select-first="true"
    closable-chips
    :hide-selected="true"
    cache-items
    :filter="itemFilter"
    item-value="id"
    :item-title="formatName"
    v-bind="attrs"
  />
</template>

<script setup lang="ts">
import {
  autocompleteDefaults,
  AutocompleteEmits,
  AutocompleteProps,
  useAutocomplete,
} from '@/components/fields/mixins/autocomplete.ts'
import {VAutocomplete} from 'vuetify/lib/components/VAutocomplete/index.mjs'
import {computed, ref, useAttrs} from 'vue'
import {useViewer} from '@/mixins/viewer.ts'
import {Character} from '@/store/characters/types/main'

const props = withDefaults(defineProps<AutocompleteProps & {newOrder?: boolean}>(), autocompleteDefaults())
const {rawViewerName} = useViewer()
const input = ref<null|typeof VAutocomplete>(null)
const attrs = useAttrs()
const extraParams = computed(() => {
  if (props.newOrder) {
    return {new_order: 'true'}
  }
  return {}
})

const emit = defineEmits<{'update:modelValue': [AutocompleteEmits]}>()
const {tags, query, items, itemFilter} = useAutocomplete({ props, emit, input, extraParams, endpoint: '/api/profiles/search/character/' })
const formatName = (_id: number, sourceItem: Character | '' | number) => {
  const item = sourceItem || _id
  /* istanbul ignore if */
  if (Array.isArray(item) || !item) {
    // Type mismatch thrown by parent library. Return an empty string for this.
    return ''
  }
  if (typeof item === 'number') {
    return `${item}`
  }
  let text = item.name
  if (item.user.username !== rawViewerName.value) {
    text += ` (${item.user.username})`
  }
  return text
}
</script>
