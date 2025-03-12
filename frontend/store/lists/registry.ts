import { createApp, markRaw } from "vue"
import { ListController } from "./controller.ts"
import { BaseRegistry, genRegistryPluginBase } from "../registry-base.ts"
import { ArtStore } from "@/store/index.ts"
import type { ListModuleOpts, ListState } from "@/store/lists/types.d.ts"

export class ListRegistry extends BaseRegistry<
  ListState<any>,
  ListController<any>
> {}

export const listRegistry = markRaw(new ListRegistry("List"))

export function createLists(store: ArtStore) {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(
        genRegistryPluginBase<
          ListState<any>,
          ListModuleOpts,
          ListController<any>
        >("List", listRegistry, ListController, store),
      )
    },
  }
}

;(window as any).listRegistry = listRegistry
