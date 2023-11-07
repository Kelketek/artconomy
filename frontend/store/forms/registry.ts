import {createApp} from 'vue'
import {FormController} from './form-controller'
import {FieldController} from './field-controller'
import {registerValidators} from './validators'
import {NamelessFormSchema} from './types/NamelessFormSchema'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base'
import {FormState} from '@/store/forms/types/FormState'

class FormRegistry extends BaseRegistry<FormState, FormController> {
  public validators: { [key: string]: (fieldController: FieldController, ...args: any[]) => string[] }
  public asyncValidators: { [key: string]: (fieldController: FieldController, ...args: any[]) => Promise<string[]> }
  constructor() {
    super()
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

export function FormControllers(app: ReturnType<typeof createApp>): void {
  app.mixin(genRegistryPluginBase<FormState, NamelessFormSchema, FormController>('Form', formRegistry, FormController))
  registerValidators()
}
