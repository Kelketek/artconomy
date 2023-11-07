import type {Ref} from 'vue'
import {ComponentOptions, createApp, h, markRaw, toValue} from 'vue'
import {BaseController, ControllerArgs} from '@/store/controller-base'
import {ArtVueInterface} from '@/types/ArtVueInterface'

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
  controllers: { [key: string]: T },
  componentMap: { [key: string]: T[] },
  uidTracking: { [key: string]: string[] },
  uidListenerTracking: {[key: string]: string[]}
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
  public uidListenerTracking: {[key: string]: string[]}
  public listeners: { [key: string]: string[] }
  constructor() {
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
    const self = this as unknown as Registry<K, T>
    const name = controller.name
    if (this.uidTracking[toValue(name)] === undefined) {
      // No references left. Controller may have been deleted outside the destroy hook.
      return
    }
    this.uidTracking[toValue(name)] = self.uidTracking[toValue(name)].filter((x) => x !== uid)
    if (this.uidTracking[toValue(name)].length === 0) {
      if (!controller.attr('persistent')) {
        if (!controller.purged) {
          controller.purge()
        }
        this.delete(toValue(controller.name))
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

export function genRegistryPluginBase<K extends AttrKeys, O, C extends BaseController<O, K>>(
  typeName: string, registry: Registry<K, C>, ControllerClass: new (args: ControllerArgs<O>) => C) {
  const base: ComponentOptions = {
    render: () => h('div'),
    methods: {},
    unmounted(): void {
      // Cleans up references to the current component in the registry.
      const self = (this as any)
      if (registry.uidListenerTracking[self._uid] !== undefined) {
        for (const listenName of registry.uidListenerTracking[self._uid]) {
          clearItem(registry.listeners, listenName, self._uid)
        }
        delete registry.uidListenerTracking[self._uid]
      }
      if (!(self._uid in registry.componentMap)) {
        return
      }
      for (const controller of registry.componentMap[self._uid]) {
        registry.unhook(self._uid, controller)
      }
      delete registry.componentMap[self._uid]
    },
  }

  function getter(this: ArtVueInterface, name: string, schema?: O, uid?: string) {
    // Convenience function which registers a module if it does not yet exist, and gets it if it does.
    // Why does TypeScript identify _uid as number? I can't find anywhere I've defined it as such, and it doesn't
    // say where it gets the declaration. It should always be string.
    uid = uid || this._uid as unknown as string
    let controller: C
    if (name in registry.controllers) {
      controller = registry.controllers[name]
      registry.register(uid, controller)
      return registry.controllers[name]
    }
    if (schema === undefined) {
      throw Error(`Attempt to pull a ${typeName} which does not exist, '${name}', from cache.`)
    }
    controller = new ControllerClass({
      initName: name, $root: this.$root, schema, $store: this.$store,
    })
    registry.register(uid, controller)
    return controller
  }

  function listener(this: ArtVueInterface, name: string, uid?: string) {
    registry.listen(uid || this._uid, name)
  }
  (base.methods as ComponentOptions<_Vue>)[`$get${typeName}`] = getter;
  (base.methods as ComponentOptions<_Vue>)[`$listenFor${typeName}`] = listener;
  (base.methods as ComponentOptions<_Vue>)[`$registryFor${typeName}`] = () => registry
  return base
}
