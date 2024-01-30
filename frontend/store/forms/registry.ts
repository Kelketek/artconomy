import {createApp} from 'vue'
import {FormController} from './form-controller'
import {FieldController} from './field-controller'
import {registerValidators} from './validators'
import {NamelessFormSchema} from './types/NamelessFormSchema'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base'
import {FormState} from '@/store/forms/types/FormState'
import {ArtStore} from '@/store'

export class FormRegistry extends BaseRegistry<FormState, FormController> {
  public validators: { [key: string]: (fieldController: FieldController, ...args: any[]) => string[] }
  public asyncValidators: { [key: string]: (fieldController: FieldController, ...args: any[]) => Promise<string[]> }
  constructor() {
    super('Form')
    this.validators = {}
    this.asyncValidators = {}
  }
  public resetValidators = () => {
    // Clears out all registered validators. Useful for tests.
    this.validators = {}
    this.asyncValidators = {}
  }
}


export const formRegistry = new FormRegistry()

export function createForms(store: ArtStore) {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(genRegistryPluginBase<FormState, NamelessFormSchema, FormController>('Form', formRegistry, FormController, store))
      registerValidators()
    }
  }
}
