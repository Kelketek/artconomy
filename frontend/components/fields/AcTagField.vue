<template>
  <v-combobox
      :chips="true"
      :multiple="true"
      v-model="tags"
      autocomplete
      v-model:search="query"
      :items="items"
      auto-select-first="exact"
      :closable-chips="true"
      ref="input"
  />
</template>

<script lang="ts">
import axios from 'axios'
import {artCall} from '@/lib/lib'
import {Component, Prop, toNative, Vue, Watch} from 'vue-facing-decorator'
import debounce from 'lodash/debounce'
import deepEqual from 'fast-deep-equal'

@Component({emits: ['update:modelValue']})
class AcTagField extends Vue {
  @Prop({required: true})
  public modelValue!: string[]

  public queryStore = ''
  public tags: string[] = []
  public oldCount = 0
  public cancelSource: AbortController = new AbortController()

  // noinspection JSMismatchedCollectionQueryUpdate
  public items: string[] = []

  public created() {
    this.tags = [...this.modelValue]
  }

  public _searchTags(val: string) {
    this.cancelSource.abort()
    this.cancelSource = new AbortController()
    artCall(
        {
          url: '/api/profiles/search/tag/',
          params: {q: val},
          method: 'get',
          signal: this.cancelSource.signal,
        },
    ).then(
        (response) => {
          this.items = response
        },
    ).catch(
        (error) => {
          if (axios.isCancel(error)) {
            return
          }
          console.error(error)
        },
    )
  }

  @Watch('modelValue', {deep: true})
  public syncDownstream(newVal: string[]) {
    this.tags = [...newVal]
  }

  @Watch('tags', {deep: true})
  public syncUpstream(newVal: string[]) {
    if (deepEqual(newVal, this.modelValue)) {
      return
    }
    this.$emit('update:modelValue', [...newVal])
    const input = this.$refs.input as any
    if (!input) {
      return
    }
    if (newVal.length !== this.oldCount) {
      this.queryStore = ''
      input.search = ''
    }
    this.oldCount = newVal.length
  }

  public get searchTags() {
    return debounce(this._searchTags, 100, {trailing: true})
  }

  public get query() {
    return this.queryStore
  }

  public set query(val: string) {
    val = val || ''
    val = val.replace(/,/g, ' ')
    val = val.replace(/\s+/g, ' ')
    const input = this.$refs.input as any
    if (val && val.split(' ').length > 1) {
      const currentSet = [...this.tags].map((item) => item.toLowerCase())
      const initialTerms = val.split(' ').filter((term) => term && !currentSet.includes(term.toLowerCase()))
      const terms: string[] = []
      const seen: { [key: string]: boolean } = {}
      for (const term of initialTerms) {
        if (seen[term.toLowerCase()]) {
          continue
        }
        seen[term.toLowerCase()] = true
        terms.push(term)
      }
      this.queryStore = ''
      input.search = ''
      this.tags.push(...terms)
      return
    }
    this.queryStore = val
    this.searchTags(val)
  }
}

export default toNative(AcTagField)
</script>
