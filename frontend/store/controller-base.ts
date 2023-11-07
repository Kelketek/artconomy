import type {Ref} from 'vue'
import {h, ref, toValue} from 'vue'
import {v4 as uuidv4} from 'uuid'
import {NullClass} from '@/store/helpers/NullClass'
import deepEqual from 'fast-deep-equal'
import {AttrKeys, Registry} from '@/store/registry-base'
import {ArtVueInterface} from '@/types/ArtVueInterface'
import {ArtStore} from '@/store/index'

export interface ControllerArgs<S> {
  initName: string,
  schema: S,
  $store: ArtStore,
  $root: ArtVueInterface,
}


export abstract class BaseController<S, D extends AttrKeys> {
  // Used by @ComputedGetters decorator
  public __getterMap: Map<any, any>
  public $store: ArtStore
  public initName!: string
  public _uid!: string
  public name: Ref<string>
  public schema: S
  public $root: ArtVueInterface
  // Set this to false if the controller never fetches anything, and so should never be waited on to load.
  public isFetchableController = true

  // Replace this with the default module new instances should be installed under, like 'lists' or 'singles'.
  public baseModuleName = 'base'

  // Name of the type of objects, like 'List' or 'Single'.
  public typeName = 'Base'

  public baseClass: any = NullClass

  // When migrating data, these keys will be excluded, expected to be handled by submodules.
  // For some reason, Array<keyof D> set as the type does not work as expected, and so we lose some type safety here.
  public submoduleKeys: string[] = []

  constructor({initName, schema, $store, $root}: ControllerArgs<S>) {
    this.__getterMap = new Map()
    this.initName = initName
    this.name = ref(initName)
    this.schema = schema
    this.$store = $store
    this._uid = uuidv4()
    this.$root = $root
  }

  public purge = (path?: string[]) => {
    path = path || this.path
    if (this.state === undefined) {
      // Already purged.
      return
    }
    for (const key of this.submoduleKeys) {
      (this as any)[key].abandon((this as any)._uid)
    }
    this.socketUnmount()
    this.kill()
    if (this.$root.$sock) {
      delete this.$root.$sock.connectListeners[`${(this as any)._uid}`]
      delete this.$root.$sock.disconnectListeners[`${(this as any)._uid}`]
    }
    this.$store.unregisterModule(path)
  }

  public kill = () => {
    // Kills any AJAX request this module is making.
    this.commit('kill')
  }

  public register = (path?: string[])=> {
    let data: Partial<D> = {}
    path = path || this.path
    if (this.$root.$sock) {
      this.$root.$sock.connectListeners[`${(this as any)._uid}`] = this.socketOpened
      this.$root.$sock.disconnectListeners[`${(this as any)._uid}`] = this.socketClosed
    }
    if (this.state) {
      if (deepEqual(path, this.path) || this.stateFor(path)) {
        // Already registered. Don't attempt to recreate the target module.
        return
      }
      data = {...this.state}
    }
    for (const key of this.submoduleKeys) {
      delete data[key as keyof D]
    }
    try {
      this.$store.registerModule(
        // eslint-disable-next-line new-cap
        path, new this.baseClass({...this.schema, ...data, ...{name: path.join('/')}}),
      )
    } catch (err) {
      console.error(
        `Failed registering ${JSON.stringify(path)}.` +
        'Likely, the parent path is not registered, but check error for more detail. It could also be an error ' +
        'in a watcher/computed property.',
      )
      throw err
    }
  }

  public get registry(): Registry<D, BaseController<S, D>> {
    // @ts-ignore
    return this.$root[`$registryFor${this.typeName}`]()
  }

  public socketOpened = () => {
    // Any calls, such as update listening registration, that the controller should make upon the socket opening should
    // be placed here.
  }

  public socketClosed = () => {

  }

  public socketUnmount = () => {
    // Any actions that should be taken when unmounting as they pertain to sockets should be placed here.
  }

  public abandon = (uid: string) => {
    this.registry.unhook(uid, this)
  }

  public migrate = (name: string) => {
    if (deepEqual(this.derivePath(name), this.path)) {
      // We're already here. Might mean that another parent module that referenced this one was updated.
      return
    }
    const oldName = this.name.value
    this.register(this.derivePath(name))
    this.name.value = name
    for (const key of this.submoduleKeys) {
      (this as any)[key].migrate(this.prefix + key)
    }
    this.registry.rename(oldName, name)
    this.$store.unregisterModule(this.derivePath(oldName))
  }

  public derivePath = (name: string) => {
    const path = name.split('/')
    if (path.length === 1) {
      path.unshift(this.baseModuleName)
    }
    return path
  }

  public get path() {
    return this.derivePath(toValue(this.name))
  }

  public stateFor = (path: string[]) => {
    const self = this as unknown as ArtVueInterface
    let state = self.$store.state as unknown
    for (const namespace of path) {
      if (state === undefined) {
        return undefined
      }
      // @ts-ignore
      state = state[namespace]
    }
    return state as undefined | D
  }

  public get state(): undefined | D {
    return this.stateFor(this.path)
  }

  public attr = <T extends keyof D>(attrName: T) => {
    return (this.state && this.state[attrName]) as D[T]
  }

  public get prefix() {
    return this.path.join('/') + '/'
  }

  public get purged() {
    return this.state === undefined
  }

  public getter = (getterName: string) => {
    return (this as unknown as ArtVueInterface).$store.getters[`${this.prefix}${getterName}`]
  }

  public commit = (mutationName: string, payload?: any) => {
    (this as unknown as ArtVueInterface).$store.commit(`${this.prefix}${mutationName}`, payload)
  }

  public dispatch = (actionName: string, payload?: any) => {
    return (this as unknown as ArtVueInterface).$store.dispatch(`${this.prefix}${actionName}`, payload)
  }

  public get socketLabelBase() {
    return `${this.typeName}Controller::${this._uid}`
  }

  // noinspection JSMethodCanBeStatic
  public render = () => {
    // Used in tests so we can mount directly.
    return h('div')
  }

  public toJSON = (): object => {
    // Used to prevent the pretty printing service from exhausting all memory.
    return {type: this.constructor.name, name: this.name, state: this.state}
  }
}
