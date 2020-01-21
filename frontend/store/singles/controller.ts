import Component from 'vue-class-component'
import {SingleModuleOpts} from './types/SingleModuleOpts'
import {SingleState} from './types/SingleState'
import {SingleModule} from './index'
import {BaseController} from '@/store/controller-base'
import {singleRegistry} from '@/store/singles/registry'
import {Patch} from '@/store/singles/patcher'
import {RawData} from '@/store/forms/types/RawData'

@Component
export class SingleController<T extends {}> extends BaseController<SingleModuleOpts<T>, SingleState<T>> {
  public baseClass = SingleModule
  public forceRecomputeCounter = 0

  // @ts-ignore
  public registry = singleRegistry

  public baseModuleName = 'singles'

  // eslint-disable-next-line camelcase
  public single_controller__ = true

  public created() {
    this.register()
  }

  public get() {
    return this.dispatch('get')
  }

  public patch(data: Partial<T>) {
    return this.dispatch('patch', data)
  }

  public delete() {
    return this.dispatch('delete')
  }

  public put(data?: any) {
    return this.dispatch('put', data)
  }

  public setX(x: T | null | false) {
    // Also available as a setter.
    if (this.x && !x) {
      this.forceRecomputeCounter += 1
    }
    this.commit('setX', x)
  }

  public getPatcher() {
    const self = this
    return new Proxy({cached: {} as {[key: string]: Patch}}, {
      get(target, propName: string) {
        if (target.cached[propName] === undefined) {
          target.cached[propName] = self.$makePatcher({modelProp: '', attrName: propName, silent: true})
        }
        return target.cached[propName]
      },
    })
  }

  public updateX(x: Partial<T>) {
    this.commit('updateX', x)
  }

  public retryGet() {
    return this.dispatch('retryGet')
  }

  public get x(): T | null | false {
    return this.attr('x')
  }

  public set x(x: T | null | false) {
    this.setX(x)
  }

  public get endpoint(): string {
    return this.attr('endpoint')
  }

  public set endpoint(val: string) {
    this.commit('setEndpoint', val)
  }

  public get fetching(): boolean {
    return this.attr('fetching')
  }

  public set fetching(val: boolean) {
    this.commit('setFetching', val)
  }

  public get ready(): boolean {
    return this.attr('ready')
  }

  public set ready(val: boolean) {
    this.commit('setReady', val)
  }

  public set params(val: RawData|null) {
    this.commit('setParams', val)
  }

  public get params() {
    return this.attr('params')
  }

  public get failed(): boolean {
    return this.attr('failed')
  }

  public refresh() {
    this.ready = false
    return this.get()
  }

  public get patchers() {
    // eslint-disable-next-line no-unused-expressions
    this.forceRecomputeCounter
    return this.getPatcher() as unknown as {[key: string]: Patch}
  }
}
