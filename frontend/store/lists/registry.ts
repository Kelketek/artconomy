import {createApp} from 'vue'
import {ListController} from './controller'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base'
import {ListState} from './types/ListState'
import {ListModuleOpts} from './types/ListModuleOpts'

class ListRegistry extends BaseRegistry<ListState<any>, ListController<any>> {}

export const listRegistry = new ListRegistry()

export function Lists(app: ReturnType<typeof createApp>): void {
  app.mixin(genRegistryPluginBase<ListState<any>, ListModuleOpts, ListController<any>>('List', listRegistry, ListController))
}


(window as any).listRegistry = listRegistry
