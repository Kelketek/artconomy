import {ListModuleOpts} from '@/store/lists/types/ListModuleOpts.ts'
import {generateModuleHooks} from '@/store/hooks.ts'
import {ListState} from '@/store/lists/types/ListState.ts'
import {ListController, RawListController} from '@/store/lists/controller.ts'

const {use, listen, clear} = generateModuleHooks<ListState<any>, ListModuleOpts, RawListController<any>>('List', RawListController)

export const useList = <T extends object>(name: string, schema?: ListModuleOpts) => use(name, schema) as ListController<T>
export const listenForList = listen
export const clearListAssociations = clear
