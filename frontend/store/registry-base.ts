import _Vue, {ComponentOptions} from 'vue'
import {Vue} from 'vue/types/vue'
import {DefaultMethods} from 'vue/types/options'
import {neutralize} from '@/lib/lib'

export interface AttrKeys {
  persistent: boolean,
}

declare interface Registerable<K extends AttrKeys> extends Vue {
  purge: () => void
  purged: boolean,
  initName: string,
  name: string,
  migrate: (newName: string) => void,
  attr: (attrName: keyof K) => any,
  socketOpened: () => void,
  socketUnmount: () => void,
}

export interface Registry<K extends AttrKeys, T extends Registerable<K>> {
  controllers: { [key: string]: T },
  componentMap: { [key: number]: T[] },
  uidTracking: { [key: string]: number[] },
  uidListenerTracking: {[key: number]: string[]}
  listeners: { [key: string]: number[] },
  register: (uid: number, controller: T) => void,
  registerSocketListeners: () => void,
  listen: (uid: number, name: string) => void,
  ignore: (uid: number, name: string) => void,
  unhook: (uid: number, controller: T) => void,
  delete: (name: string) => void,
  rename: (oldName: string, newName: string) => void,
  reset: () => void,
}

declare interface Tracker {
  [key: number]: any[],
  [key: string]: any[],
}

export function addItem(tracker: Tracker, key: number|string, value: any) {
  if (tracker[key] === undefined) {
    tracker[key] = []
  }
  if (tracker[key].indexOf(value) === -1) {
    tracker[key].push(value)
  }
}

export function clearItem(tracker: Tracker, key: number|string, value: any) {
  /* istanbul ignore if */
  if (tracker[key] === undefined) {
    return
  }
  tracker[key] = tracker[key].filter((x) => x !== value)
  if (tracker[key].length === 0) {
    delete tracker[key]
  }
}

export function genRegistryBase<K extends AttrKeys, T extends Registerable<K>>() {
  return {
    data: {
      // We're making all of these non-reactive, since the recursion is liable to cause performance problems
      // if we accidentally attach the registry somewhere.
      controllers: neutralize({}),
      componentMap: neutralize({}),
      uidTracking: neutralize({}),
      listeners: neutralize({}),
      uidListenerTracking: neutralize({}),
      socketListeners: neutralize([]),
    },
    methods: {
      register(uid: number, controller: T) {
        const self = (this as unknown as Registry<K, T>)
        self.controllers[controller.name] = controller
        const baseUIDs = []
        for (const pattern of Object.keys(self.listeners)) {
          /* istanbul ignore else */
          if (pattern === '__ob__') {
            continue
          }
          if (RegExp(pattern).test(controller.name)) {
            baseUIDs.push(...self.listeners[pattern])
          }
        }
        for (const toRegister of [...baseUIDs, uid]) {
          addItem(self.componentMap, toRegister, controller)
          addItem(self.uidTracking, controller.name, toRegister)
        }
      },
      listen(uid: number, name: string) {
        // Registers a 'listener' for a controller. This is most useful for caching-- if a parent view knows its child
        // will register a specific controller, it can be treated as though it, too, had registered the controller
        // without having to provide a schema.
        const self = (this as unknown as Registry<K, T>)
        addItem(self.listeners, name, uid)
        addItem(self.uidListenerTracking, uid, name)
      },
      ignore(uid: number, name: string) {
        // Removes a listener. Does not unhook.
        const self = (this as unknown as Registry<K, T>)
        clearItem(self.listeners, name, uid)
        clearItem(self.uidListenerTracking, uid, name)
      },
      reset() {
        // Clears all data. Useful for testing.
        const self = (this as unknown as Registry<K, T>)
        self.controllers = neutralize({})
        self.componentMap = neutralize({})
        self.uidTracking = neutralize({})
        self.listeners = neutralize({})
        self.uidListenerTracking = neutralize({})
      },
      unhook(uid: number, controller: Registerable<K>) {
        // Reference tracking for removal of controller. Deletes the Vuex representation if it is not set persistent
        // and there are no references to the form in the registry.
        const self = this as unknown as Registry<K, T>
        const name = controller.name
        if (self.uidTracking[name] === undefined) {
          // No references left. Controller may have been deleted outside of the destroy hook.
          return
        }
        self.uidTracking[name] = self.uidTracking[name].filter((x) => x !== uid)
        if (self.uidTracking[name].length === 0) {
          if (!controller.attr('persistent')) {
            if (!controller.purged) {
              controller.purge()
            }
            self.delete(controller.name)
          }
        }
      },
      rename(oldName: string, newName: string) {
        const self = this as unknown as Registry<K, T>
        if (self.controllers[oldName] === undefined) {
          return
        }
        self.controllers[newName] = self.controllers[oldName]
        delete self.controllers[oldName]
        self.uidTracking[newName] = self.uidTracking[oldName]
        delete self.uidTracking[oldName]
      },
      delete(name: string) {
        // Removes information from the registry. Most useful if the delete call happens from outside.
        const self = (this as unknown as Registry<K, T>)
        delete self.controllers[name]
        delete self.uidTracking[name]
      },
    },
  }
}

export function genRegistryPluginBase<K extends AttrKeys, O, T extends Registerable<K>>(
  typeName: string, registry: Registry<K, T>, ControllerClass: new(...args: any) => T) {
  const base: ComponentOptions<Vue> = {
    methods: {},
    destroyed(): void {
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

  function getter(this: _Vue, name: string, schema?: O) {
    // Convenience function which registers a module if it does not yet exist, and gets it if it does.
    let controller: T
    const self = (this as any)
    if (name in registry.controllers) {
      controller = registry.controllers[name]
      registry.register(self._uid, controller)
      return registry.controllers[name]
    }
    if (schema === undefined) {
      throw Error(`Attempt to pull a ${typeName} which does not exist, '${name}', from cache.`)
    }
    controller = new ControllerClass({
      store: self.$store,
      propsData: {initName: name, schema},
      parent: self,
      // I wonder how THIS is gonna change in Vue 3 >.>
      // @ts-ignore
      extends: self.$root.$options._base,
    })
    registry.register(self._uid, controller)
    return controller
  }

  function listener(this: _Vue, name: string) {
    const self = this as any
    registry.listen(self._uid, name)
  }
  // This suddenly broke but we're now replacing it with an upgraded frontend base anyway. Throwing anys in there
  // and calling it a day.
  (base.methods as ComponentOptions<any, any, any>['methods'])[`$get${typeName}`] = getter;
  (base.methods as ComponentOptions<any, any, any>['methods'])[`$listenFor${typeName}`] = listener;
  (base.methods as ComponentOptions<any, any, any>['methods'])[`$registryFor${typeName}`] = () => registry
  return base
}
