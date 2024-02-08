import {createApp} from 'vue'
import {ListController} from './controller.ts'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base.ts'
import {ListState} from './types/ListState.ts'
import {ListModuleOpts} from './types/ListModuleOpts.ts'
import {ArtStore} from '@/store/index.ts'

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
