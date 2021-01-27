import _Vue from 'vue'
import {genRegistryBase, genRegistryPluginBase, Registry} from '../registry-base'
import {SingleModuleOpts} from './types/SingleModuleOpts'
import {SingleController} from './controller'
import {SingleState} from './types/SingleState'
import {PatcherConfig, Patch} from '@/store/singles/patcher'

declare interface SingleRegistry extends Registry<SingleState<any>, SingleController<any>> {
}

export const singleRegistry = new _Vue(genRegistryBase()) as SingleRegistry

export function Singles(Vue: typeof _Vue): void {
  const base = genRegistryPluginBase('Single', singleRegistry, SingleController)
  base.data = () => {
    return {patchData: {}}
  }
  function $makePatcher(this: _Vue, config: PatcherConfig) {
    const options: any = {...config}
    options.target = this
    return new Patch({
      store: this.$store,
      propsData: options,
      parent: this,
      // I wonder how THIS is gonna change in Vue 3 >.>
      // @ts-ignore
      extends: this.$root.$options._base,
    })
  }
  base.methods!.$makePatcher = $makePatcher
  Vue.mixin(base)
}

declare module 'vue/types/vue' {
  // Global properties can be declared
  // on the `VueConstructor` interface

  interface Vue {
    $getSingle: (name: string, schema?: SingleModuleOpts<any>) => SingleController<any>,
    $listenForSingle: (name: string) => void,
    $makePatcher: (config: PatcherConfig) => Patch,
  }
}

(window as any).singleRegistry = () => singleRegistry
