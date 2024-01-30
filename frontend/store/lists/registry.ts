import {createApp} from 'vue'
import {ListController} from './controller'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base'
import {ListState} from './types/ListState'
import {ListModuleOpts} from './types/ListModuleOpts'
import {ArtStore} from '@/store'

export class ListRegistry extends BaseRegistry<ListState<any>, ListController<any>> {}

export const listRegistry = new ListRegistry('List')

export function createLists(store: ArtStore) {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(genRegistryPluginBase<ListState<any>, ListModuleOpts, ListController<any>>('List', listRegistry, ListController, store))
    }
  }
}


(window as any).listRegistry = listRegistry
