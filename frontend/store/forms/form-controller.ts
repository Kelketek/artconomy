import {FieldController} from './field-controller.ts'
import {MutationPayload} from 'vuex'
import {formRegistry} from './registry.ts'
import {deriveErrors} from './helpers.ts'
import {BaseController, ControllerArgs} from '@/store/controller-base.ts'
import {dataFromForm} from '@/store/forms/index.ts'
import {ComputedGetters, flatten} from '@/lib/lib.ts'
import {computed, effectScope, nextTick, toValue} from 'vue'

import type {AcServerError, ArtVueInterface} from '@/types/main'
import StepSpec, {FormState, NamelessFormSchema, RawData} from '@/store/forms/types/main'

export interface FieldBank {
  [key: string]: FieldController
}

// This module is the oldest of the store now. So some things may not behave as the other modules do.
// At some point we should refactor this component to behave in the same way as the rest of the modules-- with fields
// as their own component type with their own registry.
@ComputedGetters
export class FormController extends BaseController<NamelessFormSchema, FormState> {
  public fields: FieldBank = {}
  public watcherMap: { [key: string]: (mutation: MutationPayload) => void } = {}

  public baseModuleName = 'forms'

  public typeName: 'Form' = 'Form'
  // tslint:disable-next-line:no-empty
  private unsubscribe: (() => void) = null as unknown as (() => void)

  constructor(args: ControllerArgs<NamelessFormSchema>) {
    super(args)
    this.watcherMap = {
      'forms/addField': this.watchAddField,
      'forms/delField': this.watchDelField,
      'forms/delForm': this.watchDelForm,
    }
    this.$store.commit('forms/initForm', {...{name: this.name.value}, ...this.schema})
    for (const key of Object.keys(this.schema.fields)) {
      this.fields[key] = new FieldController({
        $router: this.$router,
        $registries: this.$registries,
        $sock: this.$sock,
        formName: this.name.value,
        fieldName: key,
        $store: this.$store
      })
    }
    this.unsubscribe = this.$store.subscribe(this.formWatch)
  }

  public stopValidators = () => {
    for (const key of Object.keys(this.fields)) {
      // Make sure we don't end up with lingering validation requests.
      this.fields[key].cancelValidation()
    }
  }

  public submitThen = (success: (response: any) => void, error?: (response: AcServerError) => void) => {
    error = error || this.setErrors
    return this.submit().then(success).catch(error)
  }

  public submit = () =>  {
    const self = this as unknown as ArtVueInterface
    this.stopValidators()
    return self.$store.dispatch('forms/submit', {name: this.name.value})
  }

  public reset = () => {
    const self = this as unknown as ArtVueInterface
    self.$store.commit('forms/resetForm', {name: this.name.value})
  }

  public purge = () => {
    const self = this as unknown as ArtVueInterface
    this.stopValidators()
    self.$store.commit('forms/delForm', {name: this.name.value})
  }

  public get errors() {
    if (this.purged) {
      return []
    }
    return this.attr('errors')
  }

  public set errors(errors: string[]) {
    const self = this as unknown as ArtVueInterface
    self.$store.commit('forms/setMetaErrors', {name: toValue(this.name), errors})
  }

  public get disabled(): boolean {
    return this.sending || this.attr('disabled')
  }

  public get sending(): boolean {
    return this.attr('sending')
  }

  public set sending(value: boolean) {
    // Not only used internally -- Sometimes useful when doing custom error handling.
    this.$store.commit('forms/updateMeta', {name: toValue(this.name), meta: {sending: value}})
  }

  public get bind() {
    return {errors: this.errors, sending: this.sending, id: `form-${flatten(toValue(this.name))}`}
  }

  public get rawData(): RawData {
    const self = this as unknown as ArtVueInterface
    return dataFromForm(self.$store.state.forms![toValue(this.name)])
  }

  public get endpoint() {
    return this.attr('endpoint')
  }

  public set endpoint(endpoint) {
    this.$store.commit('forms/setEndpoint', {name: toValue(this.name), endpoint})
  }

  public get step() {
    return this.attr('step')
  }

  public set step(step: number) {
    const self = this as unknown as ArtVueInterface
    self.$store.commit('forms/setStep', {name: toValue(this.name), step})
  }

  public get lastStep() {
    let step = 1
    for (const field of Object.values(this.fields)) {
      if (field.step > step) {
        step = field.step
      }
    }
    return step
  }

  public get failedSteps() {
    const steps: number[] = []
    for (const field of Object.values(this.fields)) {
      if (field.errors.length && !steps.includes(field.step)) {
        steps.push(field.step)
      }
    }
    steps.sort()
    return steps
  }

  public get steps() {
    const steps: {[key: number]: StepSpec} = {}
    const failedSteps = this.failedSteps
    for (let i = 1; i <= this.lastStep; i++) {
      const failed = failedSteps.includes(i)
      steps[i] = {
        failed,
        complete: (this.step) > i && !failed,
        rules: [() => !failed],
      }
    }
    return steps
  }

  public attr = (attrName: keyof FormState): any => {
    const form = this.$store.state.forms![this.name.value]
    return form && form[attrName]
  }

  public clearErrors = () => {
    const self = this as unknown as ArtVueInterface
    self.$store.commit('forms/clearErrors', {name: this.name.value})
  }

  public formWatch = (mutation: MutationPayload) => {
    if (this.watcherMap[mutation.type]) {
      this.watcherMap[mutation.type](mutation)
    }
  }

  public kill = () => {
    // no-op for compatibility
  }

  public watchAddField = (mutation: MutationPayload) => {
    if (mutation.payload.name !== this.name.value) {
      return
    }
    this.fields[mutation.payload.field.name] = new FieldController({
      $router: this.$router,
      $registries: this.$registries,
      $sock: this.$sock,
      formName: this.name.value,
      fieldName: mutation.payload.field.name,
      $store: this.$store,
    })
  }

  public watchDelField = (mutation: MutationPayload) => {
    if (mutation.payload.name !== this.name.value) {
      return
    }
    delete this.fields[mutation.payload.field]
    formRegistry.delete(this.name.value)
  }

  public watchDelForm = (mutation: MutationPayload) => {
    if (mutation.payload.name !== this.name.value) {
      return
    }
    this.fields = {}
    this.unsubscribe()
    formRegistry.delete(this.name.value)
  }

  public scrollToError = () => {
    let scrollables = document.querySelectorAll(`#${this.bind.id} .scrollableText`)
    if (!scrollables.length) {
      scrollables = document.querySelectorAll(`#${this.bind.id}`)
    }
    if (!scrollables.length) {
      // If this doesn't return something we're fucked anyway.
      scrollables = document.querySelectorAll('body')
    }
    const errors = scrollables[0].querySelectorAll(':scope .error--text')
    if (errors.length) {
      errors[0].scrollIntoView({behavior: 'smooth', block: 'center'})
    }
  }

  public setErrors = (error: AcServerError) => {
    this.stopValidators()
    const errorSet = deriveErrors(error, Object.keys(this.fields))
    if (errorSet.errors.length && !Object.keys(errorSet.fields).length) {
      this.$store.commit(
        'forms/setMetaErrors',
        {name: this.name.value, errors: errorSet.errors})
      this.sending = false
      return
    }
    this.$store.commit('forms/setErrors', {name: this.name.value, errors: errorSet})
    this.sending = false
    nextTick(this.scrollToError)
    return error
  }

  public toJSON = () => {
    // Used to prevent the pretty printing service from exhausting all memory.
    return {type: this.constructor.name, name: this.name.value, state: this.rawData}
  }
}
