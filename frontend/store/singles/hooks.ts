import {SingleModuleOpts} from '@/store/singles/types/SingleModuleOpts.ts'
import {generateModuleHooks} from '@/store/hooks.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {SingleState} from '@/store/singles/types/SingleState.ts'

const {use, listen, clear} = generateModuleHooks<SingleState<any>, SingleModuleOpts<any>, SingleController<any>>('Single', SingleController)

export const useSingle = <T extends object>(name: string, schema?: SingleModuleOpts<T>) => use(name, schema) as SingleController<T>
export const listenForSingle = listen
export const clearSingleAssociations = clear
