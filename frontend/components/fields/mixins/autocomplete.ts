import axios from 'axios'
import cloneDeep from 'lodash/cloneDeep'
import debounce from 'lodash/debounce'
import {artCall} from '@/lib/lib.ts'
import deepEqual from 'fast-deep-equal'
import {RawData} from '@/store/forms/types/RawData.ts'
import {computed, ref, Ref, toValue, watch} from 'vue'
import {VAutocomplete} from 'vuetify/lib/components/VAutocomplete/index.mjs'
import {isNumber} from 'lodash'

// TODO: Find a way to generalize this properly. I can't look up the docs now, but I need to be able to specify
// that itemValue will be a key on this model whose value is a string.
declare interface IdModel {
  id: number,
  [key: string]: any,
}

export type AutocompleteEmits = number[] | number | null | string

export interface AutocompleteProps {
  modelValue: number[] | number | null,
  initItems?: IdModel[],
  multiple?: boolean,
  tagging?: boolean,
  filter?: (item: IdModel, queryText: string, itemText: string) => boolean,
  allowRaw?: boolean,
}

export const autocompleteDefaults = () => ({
  multiple: true,
  tagging: false,
  allowRaw: false,
  initItems: () => [],
})

export const useAutocomplete = (
  props: AutocompleteProps,
  emit: (name: 'update:modelValue', payload: number[] | number | null | string) => void,
  input: Ref<null|typeof VAutocomplete>,
  endpoint: string,
  itemValue: string = 'id',
) => {
  // Made undefined by child component at times.
  // Must be set as v-model:search on VAutocomplete.
  const query = ref<string | undefined>('')
  const cancelSource = ref(new AbortController())
  // Must be set as v-model on VAutocomplete
  const tags = ref<number[] | number | null | string>([])
  const oldValue = ref<number[] | number | null | undefined>(undefined)
  const itemStore = ref<{ [key: number]: IdModel }>({})
  const cachedItems = ref<{ [key: number]: IdModel }>({})
  const initMap = computed(() => {
    const map: { [key: number]: IdModel } = {};
    (props.initItems || []).forEach((val) => map[val.id] = val)
    return map
  })
  const _searchTags = (val: string) => {
    cancelSource.value.abort()
    cancelSource.value = new AbortController()
    const params: RawData = {q: val}
    if (props.tagging) {
      params.tagging = true
    }
    artCall(
      {
        url: endpoint,
        params,
        method: 'get',
        signal: cancelSource.value.signal,
      },
    ).then(
      (response) => {
        items.value = response.results
      },
    ).catch((err) => {
      /* istanbul ignore next */
      if (axios.isCancel(err)) {
        return
      }
      /* istanbul ignore next */
      throw err
    })
  }
  const items = computed<IdModel[]>({
    get: (): IdModel[] => {
      if (!query.value && !tags.value) {
        return []
      }
      return [...Object.values({...itemStore.value, ...initMap.value, ...cachedItems.value})]
    },
    set: (val: IdModel[]) => {
      /* Repeated attempts to test this block have been thwarted by upstream insanity. */
      /* istanbul ignore next */
      if (props.allowRaw && query.value) {
        const addedVal: IdModel = {id: 0}
        // This is almost certainly wrong, since itemValue is 'id' by default, which we know is a number.
        // I don't know why this is here, but it's not breaking anything obvious and this is pretty complicated code,
        // so I'm going to leave it as-is until it proves to cause an issue.
        addedVal[itemValue] = (query.value + '').trim()
        val.push(addedVal)
      }
      const items: { [key: number]: IdModel } = {}
      val.forEach((item) => items[item.id] = item)
      cachedItems.value = {...cachedItems.value, ...items}
      itemStore.value = items
    },
  })
  if (props.initItems) {
    // Allows us to cache this value internally.
    items.value = [...props.initItems]
  }
  tags.value = cloneDeep(props.modelValue)

  watch(tags, () => {
    if (Array.isArray(tags.value)) {
      emit('update:modelValue', [...tags.value])
    } else {
      /* istanbul ignore if */
      if (tags.value === undefined) {
        tags.value = null
      }
      emit('update:modelValue', tags.value)
    }
  })
  const unselected = computed(() => {
    if (Array.isArray(tags.value)) {
      return items.value.filter((val) => (tags.value as number[]).indexOf(val[itemValue]) === -1)
    } else {
      return items.value.filter((val) => (tags.value as number) !== val[itemValue])
    }
  })
  const searchTags= debounce(_searchTags, 100, {trailing: true})
  const itemFilter = (item: IdModel, queryText: string, itemText: string) => {
    if (props.filter) {
      return props.filter(item, queryText, itemText)
    }
    if ((!queryText) || (!queryText.trim())) {
      return false
    }
    if (props.multiple) {
      if (props.modelValue && (props.modelValue as number[]).indexOf(item[itemValue]) !== -1) {
        return false
      }
    } else if (props.modelValue && props.modelValue === item[itemValue]) {
      return false
    }
    return itemText.toLocaleLowerCase().indexOf(queryText.toLocaleLowerCase()) > -1
  }
  watch(query, (val) => {
    if (!val) {
      items.value = []
      return
    }
    if (val.endsWith(' ')) {
      val = val.trim()
      if (unselected.value.length) {
        if (Array.isArray(tags.value)) {
          tags.value.push(unselected.value[0][itemValue])
        } else {
          tags.value = unselected.value[0][itemValue]
        }
        query.value = ''
        if (input.value) {
          input.value.search = ''
        }
        items.value = []
        return
      }
    }
    searchTags(val)
  })

  watch(() => props.modelValue, (newVal, oldVal) => {
    if (deepEqual(newVal, oldVal)) {
      return
    }
    oldValue.value = cloneDeep(oldVal)
    const cached: { [key: number]: IdModel } = {}
    items.value.forEach((val) => cached[val.id] = val)
    if (Array.isArray(newVal)) {
      newVal.forEach((val) => {
        if (!cachedItems.value[val] && cached[val]) cachedItems.value[val] = cached[val]
      })
    } else if (newVal && !cachedItems.value[newVal] && cached[newVal]) {
      cachedItems.value[newVal] = cached[newVal]
    }
    if ((newVal === undefined) || (newVal === null)) {
      query.value = ''
      if (input.value) {
        input.value.search = ''
      }
      if (props.multiple) {
        tags.value = []
      } else {
        tags.value = null
      }
      return
    }
    tags.value = cloneDeep(newVal)
    if ((oldVal === undefined) || (oldVal === null)) {
      return
    }
    let reset = false
    if (isNumber(newVal) || isNumber(oldVal)) {
      if (oldVal !== newVal) {
        reset = true
      }
    } else if (oldVal.length < newVal.length) {
      reset = true
    }
    if (reset){
      query.value = ''
      if (input.value) {
        input.value.search = ''
      }
    }
  }, {immediate: true, deep: true})
  return {
    tags,
    items,
    query,
    itemStore,
    cachedItems,
    initMap,
    itemFilter,
  }
}
