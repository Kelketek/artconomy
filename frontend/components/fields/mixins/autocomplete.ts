import {Component, Prop, Vue, Watch} from 'vue-facing-decorator'
import axios from 'axios'
import cloneDeep from 'lodash/cloneDeep'
import debounce from 'lodash/debounce'
import {artCall} from '@/lib/lib'
import deepEqual from 'fast-deep-equal'
import {RawData} from '@/store/forms/types/RawData'

declare interface IdModel {
  id: number,
  [key: string]: any,
}

@Component({emits: ['update:modelValue']})
export default class Autocomplete extends Vue {
  @Prop({required: true})
  public modelValue!: number[] | number

  @Prop({default: () => []})
  public initItems!: IdModel[]

  @Prop({default: true})
  public multiple!: boolean

  @Prop({default: false})
  public tagging!: false

  @Prop({default: null})
  public filter!: (item: IdModel, queryText: string, itemText: string) => boolean

  // Can override this to, say, username.
  @Prop({default: 'id'})
  public itemValue!: string

  // Allow a raw string to be used
  @Prop({default: false})
  public allowRaw!: boolean

  // Made null by child component at times.
  public query: string = ''
  public tags: (number[] | number | null | string) = []
  public cancelSource: AbortController = new AbortController()
  public oldValue: any = undefined
  public itemStore: { [key: number]: IdModel } = {}
  public cachedItems: { [key: number]: IdModel } = {}
  public url = '/endpoint/'

  public created() {
    if (this.initItems) {
      // Allows us to cache this value internally.
      this.items = [...this.initItems]
    }
    this.tags = cloneDeep(this.modelValue)
  }

  public _searchTags(val: string) {
    this.cancelSource.abort()
    this.cancelSource = new AbortController()
    const params: RawData = {q: val}
    if (this.tagging) {
      params.tagging = true
    }
    artCall(
      {
        url: this.url,
        params,
        method: 'get',
        signal: this.cancelSource.signal,
      },
    ).then(
      (response) => {
        this.items = response.results
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

  @Watch('tags')
  public syncUpstream() {
    if (Array.isArray(this.tags)) {
      this.$emit('update:modelValue', [...this.tags])
    } else {
      /* istanbul ignore if */
      if (this.tags === undefined) {
        this.tags = null
      }
      this.$emit('update:modelValue', this.tags)
    }
  }

  public get initMap() {
    const map: {[key: number]: IdModel} = {}
    this.initItems.forEach((val) => map[val.id] = val)
    return map
  }

  @Watch('modelValue', {
    immediate: true,
    deep: true,
  })
  public clearQuery(newVal: (number[] | null), oldVal: (number[] | null | undefined)) {
    if (deepEqual(newVal, oldVal)) {
      return
    }
    const input = this.$refs.input as any
    this.oldValue = cloneDeep(oldVal)
    const cached: {[key: number]: IdModel} = {}
    this.items.forEach((val) => cached[val.id] = val)
    if (Array.isArray(newVal)) {
      newVal.forEach((val) => {
        if (!this.cachedItems[val] && cached[val]) this.cachedItems[val] = cached[val]
      })
    } else if (newVal && !this.cachedItems[newVal] && cached[newVal]) {
      this.cachedItems[newVal] = cached[newVal]
    }
    if ((newVal === undefined) || (newVal === null)) {
      this.query = ''
      if (input) {
        input.search = ''
      }
      if (this.multiple) {
        this.tags = []
      } else {
        this.tags = null
      }
      return
    }
    this.tags = cloneDeep(newVal)
    if ((oldVal === undefined) || (oldVal === null)) {
      return
    }
    if (oldVal.length < newVal.length) {
      this.query = ''
      if (input) {
        input.search = ''
      }
    }
  }

  @Watch('query')
  public triggerSearch(val: string) {
    if (!val) {
      this.items = []
      return
    }
    if (val.endsWith(' ')) {
      const input = this.$refs.input as any
      val = val.trim()
      if (this.unselected.length) {
        if (Array.isArray(this.tags)) {
          this.tags.push(this.unselected[0][this.itemValue])
        } else {
          this.tags = this.unselected[0][this.itemValue]
        }
        this.query = ''
        if (input) {
          input.search = ''
        }
        this.items = []
        return
      }
    }
    this.searchTags(val)
  }

  public itemFilter(item: IdModel, queryText: string, itemText: string) {
    if (this.filter) {
      return this.filter(item, queryText, itemText)
    }
    if ((!queryText) || (!queryText.trim())) {
      return false
    }
    if (this.multiple) {
      if (this.modelValue && (this.modelValue as number[]).indexOf(item[this.itemValue]) !== -1) {
        return false
      }
    } else if (this.modelValue && this.modelValue === item[this.itemValue]) {
      return false
    }
    return itemText.toLocaleLowerCase().indexOf(queryText.toLocaleLowerCase()) > -1
  }

  public get fieldAttrs() {
    return {...this.$attrs}
  }

  public get items() {
    if (!this.query && !this.tags) {
      return []
    }
    return [...Object.values({...this.itemStore, ...this.initMap, ...this.cachedItems})]
  }

  public set items(val: IdModel[]) {
    /* Repeated attempts to test this block have been thwarted by upstream insanity. */
    /* istanbul ignore next */
    if (this.allowRaw && this.query) {
      const addedVal: IdModel = {id: 0}
      addedVal[this.itemValue] = (this.query + '').trim()
      val.push(addedVal)
      // Clear out our previous cached hacks here.
      // @ts-ignore
      this.$refs.input.cachedItems = this.$refs.input.cachedItems.filter((item: IdModel) => item.id !== 0)
    }
    const items: {[key: number]: IdModel} = {}
    val.forEach((item) => items[item.id] = item)
    this.itemStore = items
  }

  public get unselected() {
    if (Array.isArray(this.tags)) {
      return this.items.filter((val) => (this.tags as number[]).indexOf(val[this.itemValue]) === -1)
    } else {
      return this.items.filter((val) => (this.tags as number) !== val[this.itemValue])
    }
  }

  public get searchTags() {
    return debounce(this._searchTags, 100, {trailing: true})
  }
}
