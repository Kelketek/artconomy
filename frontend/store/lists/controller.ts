import Component from 'vue-class-component'
import {ListModuleOpts} from './types/ListModuleOpts'
import {SingleController} from '../singles/controller'
import {BaseController} from '@/store/controller-base'
import {ListState} from '@/store/lists/types/ListState'
import {ListModule} from '@/store/lists/index'
import {listRegistry} from '@/store/lists/registry'
import {PaginatedResponse} from '@/store/lists/types/PaginatedResponse'
import {QueryParams} from '@/store/helpers/QueryParams'

@Component
export class ListController<T> extends BaseController<ListModuleOpts, ListState<T>> {
  public baseClass = ListModule

  // @ts-ignore
  public registry = listRegistry

  public baseModuleName = 'lists'

  public created() {
    this.register()
  }

  public get() {
    return this.dispatch('get')
  }

  public remove(item: T) {
    this.commit('remove', item)
  }

  public replace(item: T) {
    this.commit('replace', item)
  }

  public push(...args: T[]) {
    this.commit('push', args)
  }

  public uniquePush(...args: T[]) {
    this.commit('uniquePush', args)
  }

  public post(item: Partial<T>) {
    return this.dispatch('post', item)
  }

  public postPush(item: Partial<T>) {
    this.post(item).then(this.push)
  }

  public setList(array: T[]) {
    this.commit('setList', array)
  }

  public next() {
    return this.dispatch('next')
  }

  public firstRun() {
    return this.dispatch('firstRun')
  }

  public retryGet() {
    return this.dispatch('retryGet')
  }

  public reset() {
    return this.dispatch('reset')
  }

  public grower(val: boolean) {
    // Used for visibility observer. If true, we fetch the next page.
    if (val && !this.fetching) {
      this.next().then()
    }
  }

  // We do not have a corresponding setter because we cannot be certain of type/store guarantees that way. Use the
  // setList function instead.
  public get list(): Array<SingleController<T>> {
    // Can happen if there remains a reference to this object after our system reaps it.
    if (!this.attr('refs')) {
      return []
    }
    let controllers = this.attr('refs').map((ref: string) => this.$getSingle(
      // Vestigil endpoint-- the controller may not be cached but the list should have defined it in the store.
      `${this.prefix}items/${ref}`, {endpoint: ''}
    ))
    controllers = controllers.filter((controller: SingleController<T>) => controller.x !== false)
    return controllers
  }

  public get endpoint(): string {
    return this.attr('endpoint')
  }

  public set endpoint(val: string) {
    this.commit('setEndpoint', val)
  }

  public get totalPages(): number {
    return this.getter('totalPages')
  }

  public get moreAvailable(): boolean {
    return this.getter('moreAvailable')
  }

  public get currentPage(): number {
    return this.attr('currentPage')
  }

  public set currentPage(val: number) {
    this.dispatch('getPage', val).then()
  }

  public get pageSize(): number {
    return this.attr('pageSize')
  }

  public get purged() {
    return !this.$store.state.lists[this.name]
  }

  public get grow() {
    return this.attr('grow')
  }

  public get params(): QueryParams|null {
    return this.attr('params')
  }

  public set params(params: QueryParams|null) {
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
      this.currentPage === 1 &&
      this.ready &&
      this.list.length === 0
    )
  }

  public get response() {
    return this.attr('response')
  }

  public set response(value: PaginatedResponse|null) {
    this.commit('setResponse', value)
  }

  public get failed() {
    return this.attr('failed')
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
}
