import type {Ref} from 'vue'
import {ComponentOptions, createApp, h, markRaw, toValue} from 'vue'
import {BaseController, ControllerArgs} from '@/store/controller-base'
import {ArtVueInterface} from '@/types/ArtVueInterface'
import {useStore} from 'vuex'
import {Router} from 'vue-router'
import {SocketManager} from '@/plugins/socket'
import {SingleState} from '@/store/singles/types/SingleState'
import {SingleController} from '@/store/singles/controller'
import {ListState} from '@/store/lists/types/ListState'
import {ListController} from '@/store/lists/controller'
import {FormState} from '@/store/forms/types/FormState'
import {FormController} from '@/store/forms/form-controller'
import {CharacterController} from '@/store/characters/controller'
import CharacterState from '@/store/characters/types/CharacterState'
import {ProfileController} from '@/store/profiles/controller'
import {ProfileState} from '@/store/profiles/types/ProfileState'
import {ArtStore} from '@/store/index'

type _Vue = ReturnType<typeof createApp>

export interface AttrKeys {
  persistent: boolean,
}

declare interface Registerable<K extends AttrKeys> {
  purge: () => void
  purged: boolean,
  initName: string,
  name: Ref<string>,
  migrate: (newName: string) => void,
  attr: (attrName: keyof K) => any,
  socketOpened: () => void,
  socketUnmount: () => void,
}

export interface Registry<K extends AttrKeys, T extends Registerable<K>> {
  typeName: string,
  controllers: { [key: string]: T },
  componentMap: { [key: string]: T[] },
  uidTracking: { [key: string]: string[] },
  uidListenerTracking: { [key: string]: string[] }
  listeners: { [key: string]: string[] },
  register: (uid: string, controller: T) => void,
  listen: (uid: string, name: string) => void,
  ignore: (uid: string, name: string) => void,
  unhook: (uid: string, controller: T) => void,
  delete: (name: string) => void,
  rename: (oldName: string, newName: string) => void,
  reset: () => void,
}

declare interface Tracker {
  [key: string]: any[],
}

export function addItem(tracker: Tracker, key: string, value: any) {
  if (tracker[key] === undefined) {
    tracker[key] = []
  }
  if (tracker[key].indexOf(value) === -1) {
    tracker[key].push(value)
  }
}

export function clearItem(tracker: Tracker, key: string, value: any) {
  /* istanbul ignore if */
  if (tracker[key] === undefined) {
    return
  }
  tracker[key] = tracker[key].filter((x) => x !== value)
  if (tracker[key].length === 0) {
    delete tracker[key]
  }
}

export abstract class BaseRegistry<K extends AttrKeys, T extends Registerable<K>> {
  // We're making all of these non-reactive, since the recursion is liable to cause performance problems
  // if we accidentally attach the registry somewhere.
  public controllers: { [key: string]: T }
  public componentMap: { [key: string]: T[] }
  public uidTracking: { [key: string]: string[] }
  public uidListenerTracking: { [key: string]: string[] }
  public listeners: { [key: string]: string[] }
  public typeName: string

  constructor(typeName: string) {
    this.typeName = typeName
    this.controllers = markRaw({})
    this.componentMap = markRaw({})
    this.uidTracking = markRaw({})
    this.listeners = markRaw({})
    this.uidListenerTracking = markRaw({})
    // this.socketListeners = markRaw([])
  }

  public register = (uid: string, controller: T) => {
    this.controllers[toValue(controller.name)] = controller
    const baseUIDs = []
    for (const pattern of Object.keys(this.listeners)) {
      /* istanbul ignore else */
      if (pattern === '__ob__') {
        continue
      }
      if (RegExp(pattern).test(toValue(controller.name))) {
        baseUIDs.push(...this.listeners[pattern])
      }
    }
    for (const toRegister of [...baseUIDs, uid]) {
      addItem(this.componentMap, toRegister, controller)
      addItem(this.uidTracking, toValue(controller.name), toRegister)
    }
  }
  public listen = (uid: string, name: string) => {
    // Registers a 'listener' for a controller. This is most useful for caching-- if a parent view knows its child
    // will register a specific controller, it can be treated as though it, too, had registered the controller
    // without having to provide a schema.
    addItem(this.listeners, name, uid)
    addItem(this.uidListenerTracking, uid, name)
  }
  public ignore = (uid: string, name: string) => {
    // Removes a listener. Does not unhook.
    clearItem(this.listeners, name, uid)
    clearItem(this.uidListenerTracking, uid, name)
  }
  public reset = () => {
    // Clears all data. Useful for testing.
    const self = (this as unknown as Registry<K, T>)
    self.controllers = markRaw({})
    self.componentMap = markRaw({})
    self.uidTracking = markRaw({})
    self.listeners = markRaw({})
    self.uidListenerTracking = markRaw({})
  }
  public unhook = (uid: string, controller: Registerable<K>) => {
    // Reference tracking for removal of controller. Deletes the Vuex representation if it is not set persistent
    // and there are no references to the form in the registry.
    const name = toValue(controller.name)
    if (this.uidTracking[name] === undefined) {
      // No references left. Controller may have been deleted outside the destroy hook.
      return
    }
    this.uidTracking[name] = this.uidTracking[name].filter((x) => x !== uid)
    if (this.uidTracking[name].length === 0) {
      if (!controller.attr('persistent')) {
        if (!controller.purged) {
          controller.purge()
        }
        this.delete(name)
      }
    }
  }
  public rename = (oldName: string, newName: string) => {
    if (this.controllers[oldName] === undefined) {
      return
    }
    this.controllers[newName] = this.controllers[oldName]
    delete this.controllers[oldName]
    this.uidTracking[newName] = this.uidTracking[oldName]
    delete this.uidTracking[oldName]
  }
  public delete = (name: string) => {
    // Removes information from the registry. Most useful if the delete call happens from outside.
    delete this.controllers[name]
    delete this.uidTracking[name]
  }
}

export const performUnhook = <K extends AttrKeys, S, C extends BaseController<S, K>>(uid: string, registry: Registry<K, C>) => {
  // Cleans up references to a component ID in the registry.
  if (registry.uidListenerTracking[uid] !== undefined) {
    for (const listenName of registry.uidListenerTracking[uid]) {
      clearItem(registry.listeners, listenName, uid)
    }
    delete registry.uidListenerTracking[uid]
  }
  if (!(uid in registry.componentMap)) {
    return
  }
  for (const controller of registry.componentMap[uid]) {
    registry.unhook(uid, controller)
  }
  delete registry.componentMap[uid]
}

export type ModuleName = 'Single' | 'List' | 'Form' | 'Character' | 'Profile'

export interface RegistryRegistry {
  Single: Registry<SingleState<any>, SingleController<any>>,
  List: Registry<ListState<any>, ListController<any>>,
  Form: Registry<FormState, FormController>,
  Character: Registry<CharacterState, CharacterController>,
  Profile: Registry<ProfileState, ProfileController>,
}


declare interface ControllerInvocationArgs<S, K extends AttrKeys, C extends BaseController<S, K>> {
  uid: string,
  name: string,
  schema: S | undefined,
  registries: RegistryRegistry,
  typeName: keyof RegistryRegistry,
  router: Router,
  socket: SocketManager,
  store: ArtStore,
  ControllerClass: new (args: ControllerArgs<S>) => C,
}

export const getController = <K extends AttrKeys, S, C extends BaseController<S, K>>(
{ uid, name, schema, registries, typeName, ControllerClass, socket, router, store }: ControllerInvocationArgs<S, K, C>,
): C => {
  // Convenience function which registers a module if it does not yet exist, and gets it if it does.
  // Why does TypeScript identify _uid as number? I can't find anywhere I've defined it as such, and it doesn't
  // say where it gets the declaration. It should always be string.

  let controller: C
  const registry = registries[typeName] as unknown as Registry<K, C>
  if (name in registry.controllers) {
    controller = registry.controllers[name]
    registry.register(uid, controller)
    return registry.controllers[name]
  }
  if (schema === undefined) {
    throw Error(`Attempt to pull a ${registry.typeName} which does not exist, '${name}', from cache.`)
  }
  controller = new ControllerClass({
    initName: name,
    schema,
    $sock: socket,
    $registries: registries,
    $router: router,
    $store: store,
  })
  registry.register(uid, controller)
  return controller
}

export const listenForRegistryName = <K extends AttrKeys, S, C extends BaseController<S, K>>(uid: string, name: string, registry: Registry<K, C>) => {
  registry.listen(uid, name)
}

export function genRegistryPluginBase<K extends AttrKeys, S, C extends BaseController<S, K>>(
  typeName: ModuleName, registry: Registry<K, C>, ControllerClass: new (args: ControllerArgs<S>) => C, store: ArtStore) {
  const base: ComponentOptions = {
    render: () => h('div'),
    methods: {},
    unmounted(): void {
      performUnhook<K, S, C>(this._uid, registry)
    },
  }

  function getter(this: ArtVueInterface, name: string, schema?: S, uid?: string) {
    uid = uid || this._uid as unknown as string
    return getController<K, S, C>({
      uid,
      name,
      typeName: typeName,
      schema,
      store,
      router: this.$router,
      socket: this.$sock,
      registries: this.$registries,
      ControllerClass,
    })
  }

  function listener(this: ArtVueInterface, name: string, uid?: string) {
    listenForRegistryName<K, S, C>(uid || this._uid, name, registry)
  }

  (base.methods as ComponentOptions<_Vue>)[`$get${typeName}`] = getter;
  (base.methods as ComponentOptions<_Vue>)[`$listenFor${typeName}`] = listener;
  (base.methods as ComponentOptions<_Vue>)[`$registryFor${typeName}`] = () => registry
  return base
}
