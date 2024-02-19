import {Watch} from 'vue-facing-decorator'
import {ListModuleOpts} from './types/ListModuleOpts.ts'
import {SingleController} from '../singles/controller.ts'
import {BaseController, ControllerArgs} from '@/store/controller-base.ts'
import {ListState} from '@/store/lists/types/ListState.ts'
import {ListModule, pageFromParams, pageSizeFromParams, totalPages} from '@/store/lists/index.ts'
import {PaginatedResponse} from '@/store/lists/types/PaginatedResponse.ts'
import {QueryParams} from '@/store/helpers/QueryParams.ts'
import {ListSocketSettings} from '@/store/lists/types/ListSocketSettings.ts'
import {ComputedGetters} from '@/lib/lib.ts'
import {getController} from '@/store/registry-base.ts'
import {SingleState} from '@/store/singles/types/SingleState.ts'
import {SingleModuleOpts} from '@/store/singles/types/SingleModuleOpts.ts'
import {effectScope} from 'vue'

@ComputedGetters
export class ListController<T extends object> extends BaseController<ListModuleOpts, ListState<T>> {
  public __getterMap = new Map()
  public scope = effectScope(true)
  public baseClass = ListModule

  public baseModuleName = 'lists'

  public typeName: 'List' = 'List'

  constructor(args: ControllerArgs<ListModuleOpts>) {
    super(args)
    this.register()
  }

  public get = () => {
    return this.dispatch('get')
  }

  public remove = (item: T) => {
    this.commit('remove', item)
  }

  public replace = (item: T) => {
    this.commit('replace', item)
  }

  public unshift = (...args: T[]) => {
    this.commit('unshift', args)
  }

  public push = (...args: T[]) => {
    this.commit('push', args)
  }

  public uniquePush = (...args: T[]) => {
    this.commit('uniquePush', args)
  }

  public post = (item: Partial<T>) => {
    return this.dispatch('post', item)
  }

  public postPush = (item: Partial<T>) => {
    this.post(item).then(this.push)
  }

  public setList = (array: T[]) => {
    this.commit('setList', array)
  }

  public next = () => {
    return this.dispatch('next')
  }

  public firstRun = () => {
    return this.dispatch('firstRun')
  }

  public retryGet = () => {
    return this.dispatch('retryGet')
  }

  public makeReady = (array: T[]) => {
    this.setList(array)
    this.fetching = false
    this.ready = true
  }

  public reset = () => {
    return this.dispatch('reset')
  }

  public grower = (val: boolean) => {
    // Used for visibility observer. If true, we fetch the next page.
    if (val && !this.fetching) {
      this.next().then()
    }
  }

  // We do not have a corresponding setter because we cannot be certain of type/store guarantees that way. Use the
  // setList function instead.
  public get list(): Array<SingleController<T>> {
    // Can happen if there remains a reference to this object after our system reaps it.
    /* istanbul ignore if */
    if (!this.attr('refs')) {
      return []
    }
    let controllers = this.attr('refs').map((ref: string) => (
      getController<SingleState<T>, SingleModuleOpts<T>, SingleController<T>>(
        {
          uid: this._uid,
          name: `${this.prefix}items/${ref}`,
// Vestigial endpoint-- the controller may not be cached but the list should have defined it in the store.
          schema: {endpoint: ''},
          typeName: 'Single',
          socket: this.$sock,
          router: this.$router,
          store: this.$store,
          registries: this.$registries,
          ControllerClass: SingleController,
        },
      )))
    controllers = controllers.filter((controller: SingleController<T>) => !(controller.deleted) && !(controller.x === null))
    return controllers
  }

  public get endpoint(): string {
    return this.attr('endpoint')
  }

  public set endpoint(val: string) {
    this.commit('setEndpoint', val)
  }

  public get totalPages(): number {
    return totalPages(this.state && this.state.response)
  }

  public get moreAvailable(): boolean {
    return (!this.fetching) && (this.totalPages > this.currentPage)
  }

  public get currentPage(): number {
    return pageFromParams(this.attr('params'))
  }

  public set currentPage(val: number) {
    this.dispatch('getPage', val).then()
  }

  public get pageSize(): number {
    return pageSizeFromParams(this.attr('params'))
  }

  public get grow() {
    return this.attr('grow')
  }

  public set grow(val: boolean) {
    // Should only be used during testing, since state can't be guaranteed sane if set at runtime.
    this.commit('setGrow', val)
  }

  public get reverse() {
    return this.attr('reverse')
  }

  public get params(): QueryParams | null {
    return this.attr('params')
  }

  public set params(params: QueryParams | null) {
    this.commit('setParams', params)
  }

  public get fetching() {
    return this.attr('fetching')
  }

  public set fetching(val: boolean) {
    // Used during testing.
    this.commit('setFetching', val)
  }

  public get empty() {
    return (
      (!this.paginated || (this.currentPage === 1)) &&
      this.ready &&
      this.list.length === 0
    )
  }

  public get response() {
    return this.attr('response')
  }

  public set response(value: PaginatedResponse | null) {
    this.commit('setResponse', value)
  }

  public get failed() {
    return this.attr('failed')
  }

  public get paginated() {
    return this.attr('paginated')
  }

  public get count() {
    return this.response && this.response.count
  }

  public get ready() {
    return this.attr('ready')
  }

  public set ready(val: boolean) {
    this.commit('setReady', val)
  }

  public get stale(): boolean {
    return this.attr('stale')
  }

  public set stale(val: boolean) {
    this.commit('setStale', val)
  }

  public get keyProp() {
    return this.attr('keyProp')
  }

  @Watch('ready', {immediate: true})
  public startWatcher(currentValue: boolean) {
    if (currentValue) {
      this.socketOpened()
    }
  }

  public get socketSettings(): ListSocketSettings | null {
    return this.attr('socketSettings')
  }

  public set socketSettings(val: ListSocketSettings | null) {
    this.commit('setSocketSettings', val)
  }

  public get socketNewItemParams() {
    const socketSettings = this.attr('socketSettings')

    if (!socketSettings) {
      return null
    }
    let pk = socketSettings.list.pk
    if (pk) {
      pk = `${pk}`
    }
    return {
      app_label: socketSettings.list.appLabel,
      model_name: socketSettings.list.modelName,
      serializer: socketSettings.serializer,
      pk: pk || undefined,
      list_name: socketSettings.list.listName,
    }
  }

  public get newItemLabel() {
    const data = this.socketNewItemParams
    if (!data) {
      return ''
    }
    let pathName = `${data.app_label}.${data.model_name}`
    if (data.pk) {
      pathName += `.pk.${data.pk}`
    }
    return `${pathName}.${data.list_name}.${data.serializer}.new`
  }

  public socketUnmount = () => {
    const newItemLabel = this.newItemLabel
    if (!this.$sock?.socket) {
      return
    }
    /* istanbul ignore else */
    if (newItemLabel) {
      this.$sock.send('clear_watch_new', this.socketNewItemParams)
      this.$sock.removeListener(newItemLabel, `${this.socketLabelBase}.new`)
    }
  }

  public socketOpened = () => {
    const data = this.socketNewItemParams
    if (!this.$sock?.socket || !data || !this.ready) {
      return
    }
    if (this.stale) {
      this.ready = false
      this.get().then(() => undefined)
      this.stale = false
      return
    }
    this.$sock.addListener(
      this.newItemLabel,
      `${this.socketLabelBase}.new`,
      this.uniquePush,
    )
    this.$sock.send('watch_new', data)
  }

  public socketClosed = () => {
    this.stale = true
  }
}
