<template>
  <v-combobox
      chips
      multiple
      v-model="tags"
      autocomplete
      v-bind:search-input.sync="query"
      :items="items"
      auto-select-first
      deletable-chips
      hide-selected
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
import {cloneDeep, debounce} from 'lodash'

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
        {url: `/api/profiles/v1/search/tag/`, params: {q: val}, method: 'get', cancelToken: this.cancelSource.token}
      ).then(
        (response) => { this.items = response }
      )
    }

    @Watch('tags')
    private syncUpstream() {
      if (typeof this.tags === 'string') {
        // Weird case that happens with some older browsers.
        let val = this.tags as string
        val = this.prepVal(val)
        if (!val) {
          // Put it back to how it was.
          Vue.set(this, 'tags', [...this.value])
          this.query = ''
          return
        }
        const newVal = [...this.value]
        newVal.push(val)
        Vue.set(this, 'tags', newVal)
        this.query = ''
        return
      }
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

    private get query() {
      return this.queryStore
    }

    private prepVal(val: string) {
      val = val.replace(/\s+/g, '')
      val = val.replace(/,/g, '')
      return val.trim()
    }

    private set query(val: string) {
      val = val || ''
      let prepped = this.prepVal(val)
      if (val.endsWith(' ') && prepped) {
        this.queryStore = ''
        if (this.tags.indexOf(prepped) === -1) {
          this.tags.push(prepped)
        }
        return
      }
      this.queryStore = val
      this.searchTags(val)
    }
}
</script>
