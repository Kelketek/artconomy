import _Vue from 'vue'
import {ListController} from './controller'
import {genRegistryBase, genRegistryPluginBase, Registry} from '../registry-base'
import {ListState} from './types/ListState'
import {ListModuleOpts} from './types/ListModuleOpts'

declare interface ListRegistry extends Registry<ListState<any>, ListController<any>> {
}

export const listRegistry = new _Vue(genRegistryBase()) as ListRegistry

export function Lists(Vue: typeof _Vue): void {
  Vue.mixin(genRegistryPluginBase('List', listRegistry, ListController))
}

declare module 'vue/types/vue' {
  // Global properties can be declared
  // on the `VueConstructor` interface

  interface Vue {
    $getList: (name: string, schema?: ListModuleOpts) => ListController<any>,
    $listenForList: (name: string) => void,
  }
}

(window as any).listRegistry = listRegistry
