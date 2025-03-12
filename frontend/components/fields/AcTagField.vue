<template>
  <v-combobox
    ref="input"
    v-model="tags"
    v-model:search="query"
    :chips="true"
    :multiple="true"
    autocomplete
    :items="items"
    auto-select-first="exact"
    :closable-chips="true"
  />
</template>

<script setup lang="ts">
import axios from "axios"
import { artCall } from "@/lib/lib.ts"
import debounce from "lodash/debounce"
import deepEqual from "fast-deep-equal"
import { computed, ref, watch } from "vue"
import { VCombobox } from "vuetify/lib/components/index.mjs"

const emit = defineEmits<{ "update:modelValue": [string[]] }>()
const props = defineProps<{ modelValue: string[] }>()
const queryStore = ref("")
const tags = ref<string[]>([...props.modelValue])
const oldCount = ref(0)
const cancelSource = ref(new AbortController())
const items = ref<string[]>([])
const input = ref<null | typeof VCombobox>()

const _searchTags = (val: string) => {
  cancelSource.value.abort()
  cancelSource.value = new AbortController()
  artCall({
    url: "/api/profiles/search/tag/",
    params: { q: val },
    method: "get",
    signal: cancelSource.value.signal,
  })
    .then((response) => {
      items.value = response
    })
    .catch((error) => {
      if (axios.isCancel(error)) {
        return
      }
      console.error(error)
    })
}

const searchTags = debounce(_searchTags, 100, { trailing: true })

const query = computed({
  get: () => queryStore.value,
  set: (val) => {
    val = val || ""
    val = val.replace(/,/g, " ")
    val = val.replace(/\s+/g, " ")
    if (val && val.split(" ").length > 1) {
      const currentSet = [...tags.value].map((item) => item.toLowerCase())
      const initialTerms = val
        .split(" ")
        .filter((term) => term && !currentSet.includes(term.toLowerCase()))
      const terms: string[] = []
      const seen: { [key: string]: boolean } = {}
      for (const term of initialTerms) {
        if (seen[term.toLowerCase()]) {
          continue
        }
        seen[term.toLowerCase()] = true
        terms.push(term)
      }
      queryStore.value = ""
      if (input.value) {
        input.value.search = ""
      }
      tags.value.push(...terms)
      return
    }
    queryStore.value = val
    searchTags(val)
  },
})

watch(
  () => props.modelValue,
  (newVal) => {
    tags.value = [...newVal]
  },
  { deep: true },
)

watch(
  tags,
  (newVal) => {
    if (deepEqual(newVal, props.modelValue)) {
      return
    }
    emit("update:modelValue", [...newVal])
    if (!input.value) {
      return
    }
    if (newVal.length !== oldCount.value) {
      queryStore.value = ""
      input.value.search = ""
    }
    oldCount.value = newVal.length
  },
  { deep: true },
)
</script>
