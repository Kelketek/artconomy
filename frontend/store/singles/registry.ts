import { createApp, markRaw } from "vue"
import { BaseRegistry, genRegistryPluginBase } from "../registry-base.ts"
import { SingleController } from "./controller.ts"
import { ArtStore } from "@/store/index.ts"
import type { SingleModuleOpts, SingleState } from "@/store/singles/types.d.ts"

export class SingleRegistry extends BaseRegistry<
  SingleState<any>,
  SingleController<any>
> {}

export const singleRegistry = markRaw(new SingleRegistry("Single"))

export function createSingles(store: ArtStore) {
  const base = genRegistryPluginBase<
    SingleState<any>,
    SingleModuleOpts<any>,
    SingleController<any>
  >("Single", singleRegistry, SingleController, store)
  base.data = () => {
    return { patchData: {} }
  }
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(base)
    },
  }
}

;(window as any).singleRegistry = singleRegistry
