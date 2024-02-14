import {createApp} from 'vue'
import {RawListController} from './controller.ts'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base.ts'
import {ListState} from './types/ListState.ts'
import {ListModuleOpts} from './types/ListModuleOpts.ts'
import {ArtStore} from '@/store/index.ts'

export class ListRegistry extends BaseRegistry<ListState<any>, RawListController<any>> {}

export const listRegistry = new ListRegistry('List')

export function createLists(store: ArtStore) {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(genRegistryPluginBase<ListState<any>, ListModuleOpts, RawListController<any>>('List', listRegistry, RawListController, store))
    }
  }
}


(window as any).listRegistry = listRegistry
