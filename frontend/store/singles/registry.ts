import {createApp} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base.ts'
import {RawSingleController} from './controller.ts'
import {SingleState} from './types/SingleState.ts'
import {SingleModuleOpts} from '@/store/singles/types/SingleModuleOpts.ts'
import {ArtStore} from '@/store/index.ts'

export class SingleRegistry extends BaseRegistry<SingleState<any>, RawSingleController<any>> {}

export const singleRegistry = new SingleRegistry('Single')

export function createSingles(store: ArtStore) {
  const base = genRegistryPluginBase<SingleState<any>, SingleModuleOpts<any>, RawSingleController<any>>('Single', singleRegistry, RawSingleController, store)
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
