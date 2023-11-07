import {createApp} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base'
import {SingleController} from './controller'
import {SingleState} from './types/SingleState'
import {Patch, PatcherConfig} from '@/store/singles/patcher'
import {SingleModuleOpts} from '@/store/singles/types/SingleModuleOpts'

export class SingleRegistry extends BaseRegistry<SingleState<any>, SingleController<any>> {}

export const singleRegistry = new SingleRegistry()

export function Singles(app: ReturnType<typeof createApp>): void {
  const base = genRegistryPluginBase<SingleState<any>, SingleModuleOpts<any>, SingleController<any>>('Single', singleRegistry, SingleController)
  base.data = () => {
    return {patchData: {}}
  }
  function $makePatcher(this: ReturnType<typeof createApp>, config: PatcherConfig) {
    const options: any = {target: this, ...config}
    return new Patch(options)
  }
  base.methods!.$makePatcher = $makePatcher
  // @ts-ignore
  app.mixin(base)
}

(window as any).singleRegistry = singleRegistry
