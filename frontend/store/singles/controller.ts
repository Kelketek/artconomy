import {SingleModuleOpts} from './types/SingleModuleOpts.ts'
import {SingleState} from './types/SingleState.ts'
import {SingleModule} from './index.ts'
import {BaseController, ControllerArgs} from '@/store/controller-base.ts'
import {RawData} from '@/store/forms/types/RawData.ts'
import {SinglePatchers} from '@/store/singles/types/SinglePatchers.ts'
import {Patch, RawPatch} from '@/store/singles/patcher.ts'
import {Watch} from 'vue-facing-decorator'
import {SingleSocketSettings} from '@/store/singles/types/SingleSocketSettings.ts'
import {reactive, ref} from 'vue'
import {ComputedGetters} from '@/lib/lib.ts'
import {ShallowReactive} from 'vue'

@ComputedGetters
export class RawSingleController<T extends object> extends BaseController<SingleModuleOpts<T>, SingleState<T>> {
  public baseClass = SingleModule
  public forceRecomputeCounter = ref(0)

  public baseModuleName = 'singles'

  public typeName: 'Single' = 'Single'

  // eslint-disable-next-line camelcase
  public single_controller__ = true

  constructor(args: ControllerArgs<SingleModuleOpts<T>>) {
    super(args)
    this.register()
  }

  public get = () => {
    return this.dispatch('get')
  }

  public patch = (data: Partial<T>) => {
    return this.dispatch('patch', data)
  }

  public post = (data?: any) => {
    return this.dispatch('post', data)
  }

  public delete = () => {
    return this.dispatch('delete')
  }

  public markDeleted = () => {
    this.socketUnmount()
    this.deleted = true
    this.ready = false
    this.x = null
  }

  public put = (data?: any) => {
    return this.dispatch('put', data)
  }

  @Watch('ready', {immediate: true})
  public startWatcher = (currentValue: boolean) => {
    if (currentValue) {
      this.socketOpened()
    }
  }

  public setX = (x: T | null) => {
    this.commit('setX', x)
  }

  public getPatcher = (): SinglePatchers<T> => {
    const self = this
    return new Proxy<SinglePatchers<T>>({cached: {} as SinglePatchers<T>} as SinglePatchers<T>, {
      get(target, propName): Patch {
        const intermediary = target as {cached: SinglePatchers<T>}
        if (intermediary.cached[propName as keyof T] === undefined) {
          intermediary.cached[propName as keyof T] = new RawPatch({target: self, modelProp: '', attrName: propName as string, silent: true})
        }
        return reactive(intermediary.cached[propName as keyof T])
      },
    })
  }

  public updateX = (x: Partial<T>) => {
    this.commit('updateX', x)
  }

  public retryGet = () => {
    return this.dispatch('retryGet')
  }

  public get x(): T | null {
    return this.attr('x')
  }

  public set x(x: T | null) {
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

  public get socketSettings(): SingleSocketSettings|null {
    return this.attr('socketSettings')
  }

  public set socketSettings(val: SingleSocketSettings|null) {
    this.commit('setSocketSettings', val)
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

  public makeReady = (val: T) => {
    // For tests or preloading. Sets X and clears status flags.
    this.setX(val)
    this.ready = true
    this.fetching = false
  }

  public get patchers(): SinglePatchers<T> {
    // eslint-disable-next-line no-unused-expressions
    this.forceRecomputeCounter.value
    return this.getPatcher()
  }

  public get deleted(): boolean {
    return this.attr('deleted')
  }

  public set deleted(val: boolean) {
    this.commit('setDeleted', val)
  }

  public get socketUpdateParams() {
    const socketSettings = this.attr('socketSettings')
    if (!socketSettings || !this.x) {
      return null
    }
    const pk = this.x[(socketSettings.keyField || 'id') as keyof T]
    if (!pk) {
      return null
    }
    return {
      app_label: socketSettings.appLabel,
      model_name: socketSettings.modelName,
      serializer: socketSettings.serializer,
      pk: `${pk}`,
    }
  }

  public get updateLabel() {
    const data = this.socketUpdateParams
    if (!data) {
      return ''
    }
    return `${data.app_label}.${data.model_name}.update.${data.serializer}.${data.pk}`
  }

  public get deleteLabel() {
    const data = this.socketUpdateParams
    if (!data) {
      return ''
    }
    return `${data.app_label}.${data.model_name}.delete.${data.pk}`
  }

  public socketOpened = () => {
    const data = this.socketUpdateParams
    if (!this.$sock?.socket || !data) {
      return
    }
    this.$sock.addListener(
      this.updateLabel,
      `${this.socketLabelBase}.update`,
      // Use update to update in place so that we don't have to recompute everything.
      // Also because some weirdness happens with reference changes.
      this.updateX,
    )
    this.$sock.addListener(
      this.deleteLabel,
      `${this.socketLabelBase}.delete`,
      // Use update to update in place so that we don't have to recompute everything.
      // Also because some weirdness happens with reference changes.
      this.markDeleted,
    )
    this.$sock.send('watch', data)
  }

  public socketUnmount = () => {
    const updateLabel = this.updateLabel
    if (!this.$sock?.socket) {
      return
    }
    if (this.updateLabel) {
      this.$sock.send('clear_watch', this.socketUpdateParams)
      this.$sock.removeListener(updateLabel, `${this.socketLabelBase}.update`)
    }
    if (this.deleteLabel) {
      this.$sock.removeListener(this.deleteLabel, `${this.socketLabelBase}.delete`)
    }
  }
}

export type SingleController<T extends object> = ShallowReactive<RawSingleController<T>>
