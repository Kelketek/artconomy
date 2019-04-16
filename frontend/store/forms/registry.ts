import _Vue from 'vue'
import {FormController} from './form-controller'
import {FieldController} from './field-controller'
import {registerValidators} from './validators'
import {NamelessFormSchema} from './types/NamelessFormSchema'
import {genRegistryBase, genRegistryPluginBase, Registry} from '../registry-base'
import {FormState} from '@/store/forms/types/FormState'

declare interface FormRegistry extends Registry<FormState, FormController> {
  validators: { [key: string]: (fieldController: FieldController, ...args: any[]) => string[] },
  asyncValidators: { [key: string]: (fieldController: FieldController, ...args: any[]) => Promise<string[]> },
  resetValidators: () => void,
  resetComponentMap: () => void,
}

const registryBase = genRegistryBase()

registryBase.data = {...registryBase.data, ...{validators: {}, asyncValidators: {}}}
registryBase.methods = {
  ...registryBase.methods,
  ...{
    resetValidators() {
      // Clears out all registered validators. Useful for tests.
      const self = (this as unknown as FormRegistry)
      self.validators = {}
      self.asyncValidators = {}
    },
  },
}

export const formRegistry = new _Vue(registryBase) as FormRegistry

declare module 'vue/types/vue' {
  // Global properties can be declared
  // on the `VueConstructor` interface

  interface Vue {
    $getForm: (name: string, formSchema?: NamelessFormSchema) => FormController,
    $listenForForm: (name: string) => void,
  }
}

export function FormControllers(Vue: typeof _Vue): void {
  const registry = formRegistry as FormRegistry
  Vue.mixin(genRegistryPluginBase('Form', registry, FormController))
  registerValidators()
}
