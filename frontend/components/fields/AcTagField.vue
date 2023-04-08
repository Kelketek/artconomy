<template>
  <v-combobox
      chips
      multiple
      v-model="tags"
      autocomplete
      :search-input.sync="query"
      :items="items"
      auto-select-first
      deletable-chips
      ref="input"
      v-bind="fieldAttrs"
  />
</template>

<script lang="ts">
import Vue from 'vue'
import axios, {CancelTokenSource} from 'axios'
import {artCall} from '@/lib/lib'
import {Prop, Watch} from 'vue-property-decorator'
import Component from 'vue-class-component'
import cloneDeep from 'lodash/cloneDeep'
import debounce from 'lodash/debounce'

  @Component
export default class AcTagField extends Vue {
    @Prop({required: true})
    public value!: string[]

    private queryStore = ''
    private tags: string[] = []
    private oldCount = 0
    private cancelSource: CancelTokenSource = axios.CancelToken.source()

    // noinspection JSMismatchedCollectionQueryUpdate
    private items: string[] = []

    public created() {
      this.tags = cloneDeep(this.value)
    }

    private _searchTags(val: string) {
      this.cancelSource.cancel()
      this.cancelSource = axios.CancelToken.source()
      artCall(
        {url: '/api/profiles/v1/search/tag/', params: {q: val}, method: 'get', cancelToken: this.cancelSource.token},
      ).then(
        (response) => { this.items = response },
      ).catch(
        (error) => {
          if (axios.isCancel(error)) {
            return
          }
          console.error(error)
        },
      )
    }

    @Watch('tags')
    private syncUpstream() {
      this.$emit('input', this.tags)
      if (this.tags.length !== this.oldCount) {
        this.queryStore = ''
      }
      this.oldCount = this.tags.length
    }

    private get fieldAttrs() {
      return {...this.$attrs}
    }

    private get searchTags() {
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
        const seen: {[key: string]: boolean} = {}
        for (const term of initialTerms) {
          if (seen[term.toLowerCase()]) {
            continue
          }
          seen[term.toLowerCase()] = true
          terms.push(term)
        }
        this.queryStore = ''
        input.internalSearch = ''
        this.tags.push(...terms)
        return
      }
      this.queryStore = val
      this.searchTags(val)
    }
}
</script>
