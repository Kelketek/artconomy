import {createApp} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base'
import {SingleController} from './controller'
import {SingleState} from './types/SingleState'
import {SingleModuleOpts} from '@/store/singles/types/SingleModuleOpts'
import {ArtStore} from '@/store'

export class SingleRegistry extends BaseRegistry<SingleState<any>, SingleController<any>> {}

export const singleRegistry = new SingleRegistry('Single')

export function createSingles(store: ArtStore) {
  const base = genRegistryPluginBase<SingleState<any>, SingleModuleOpts<any>, SingleController<any>>('Single', singleRegistry, SingleController, store)
  base.data = () => {
    return {patchData: {}}
  }
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(base)
    }
  }
}

(window as any).singleRegistry = singleRegistry
