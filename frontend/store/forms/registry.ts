import {createApp, markRaw} from 'vue'
import {FormController} from './form-controller.ts'
import {FieldController} from './field-controller.ts'
import {registerValidators} from './validators.ts'
import {NamelessFormSchema} from './types/NamelessFormSchema.ts'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base.ts'
import {FormState} from '@/store/forms/types/FormState.ts'
import {ArtStore} from '@/store/index.ts'

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


export const formRegistry = markRaw(new FormRegistry())

export function createForms(store: ArtStore) {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(genRegistryPluginBase<FormState, NamelessFormSchema, FormController>('Form', formRegistry, FormController, store))
      registerValidators()
    }
  }
}
