import { generateModuleHooks } from "@/store/hooks.ts"
import { ListController } from "@/store/lists/controller.ts"
import type { ListModuleOpts, ListState } from "@/store/lists/types.d.ts"

const { use, listen, clear } = generateModuleHooks<
  ListState<any>,
  ListModuleOpts,
  ListController<any>
>("List", ListController)

export const useList = <T extends object>(
  name: string,
  schema?: ListModuleOpts,
) => use(name, schema) as ListController<T>
export const listenForList = listen
export const clearListAssociations = clear
