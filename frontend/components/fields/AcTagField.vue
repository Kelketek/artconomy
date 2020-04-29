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
        this.tags = [this.tags]
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

    private set query(val: string) {
      val = val || ''
      if (val.endsWith(' ') && val.trim()) {
        this.queryStore = ''
        val = val.replace(/\s+/g, '')
        val = val.replace(/,/g, '')
        if (this.tags.indexOf(val) === -1) {
          this.tags.push(val)
        }
        return
      }
      this.queryStore = val
      this.searchTags(val)
    }
}
</script>
