import {SingleModuleOpts} from '@/store/singles/types'
import {mount, VueMountOptions} from '@/specs/helpers'
import {SingleController} from '@/store/singles/controller.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {ListModuleOpts} from '@/store/lists/types'
import {ListController} from '@/store/lists/controller.ts'
import {NamelessFormSchema} from '@/store/forms/types/main'
import {FormController} from '@/store/forms/form-controller.ts'
import {CharacterModuleOpts} from '@/store/characters/types/main'
import {CharacterController} from '@/store/characters/controller.ts'

// Helper versions of hooks which will instantiate an empty vue object and return the relevant controller.

export const getCharacter = (name: string, schema: CharacterModuleOpts|undefined, context: VueMountOptions): CharacterController => {
  const empty = mount(Empty, context)
  return empty.vm.$getCharacter(name, schema)
}

export const getSingle = <T extends object>(name: string, schema: SingleModuleOpts<T>|undefined, context: VueMountOptions): SingleController<T> => {
  const empty = mount(Empty, context)
  return empty.vm.$getSingle(name, schema)
}

export const getList = <T extends object>(name: string, schema: ListModuleOpts|undefined, context: VueMountOptions): ListController<T> => {
  const empty = mount(Empty, context)
  return empty.vm.$getList(name, schema)
}

export const getForm = (name: string, schema: NamelessFormSchema|undefined, context: VueMountOptions): FormController => {
  const empty = mount(Empty, context)
  return empty.vm.$getForm(name, schema)
}
