import Vue, {ComponentOptions} from 'vue'
import {FieldController} from './field-controller'
import {MutationPayload} from 'vuex'
import {formRegistry} from './registry'
import Component from 'vue-class-component'
import {AxiosError} from 'axios'
import {deriveErrors} from './helpers'
import {NamelessFormSchema} from './types/NamelessFormSchema'
import {BaseController} from '@/store/controller-base'
import {dataFromForm} from '@/store/forms/index'
import StepSpec from '@/store/forms/types/StepSpec'
import {FormState} from '@/store/forms/types/FormState'
import {RawData} from '@/store/forms/types/RawData'

export interface FieldBank {
  [key: string]: FieldController
}

// This module is the oldest of the store now. So some things may not behave as the other modules do.
// At some point we should refactor this component to behave in the same way as the rest of the modules-- with fields
// as their own component type with their own registry.
@Component
export class FormController extends BaseController<NamelessFormSchema, FormState> {
  public fields: FieldBank = {}
  public watcherMap: { [key: string]: (mutation: MutationPayload) => void } = {}

  // @ts-ignore
  public registry = formRegistry

  public baseModuleName = 'forms'
  // tslint:disable-next-line:no-empty
  private unsubscribe: (() => void) = null as unknown as (() => void)

  public created() {
    this.watcherMap = {
      'forms/addField': this.watchAddField,
      'forms/delField': this.watchDelField,
      'forms/delForm': this.watchDelForm,
    }
    this.$store.commit('forms/initForm', {...{name: this.name}, ...this.schema})
    for (const key of Object.keys(this.schema.fields)) {
      const options: ComponentOptions<Vue> = {
        store: this.$store,
        propsData: {formName: this.name, fieldName: key},
        parent: this,
        // I wonder how THIS is gonna change in Vue 3 >.>
        // @ts-ignore
        extends: this.$root.$options._base,
      }
      Vue.set(this.fields, key, new FieldController(options))
    }
    this.unsubscribe = this.$store.subscribe(this.formWatch)
  }

  public stopValidators() {
    for (const key of Object.keys(this.fields)) {
      // Make sure we don't end up with lingering validation requests.
      this.fields[key].cancelValidation()
    }
  }

  public submitThen(success: (response: any) => void, error?: (response: AxiosError) => void) {
    error = error || this.setErrors
    return this.submit().then(success).catch(error)
  }

  public submit() {
    this.stopValidators()
    return this.$store.dispatch('forms/submit', {name: this.name})
  }

  public reset() {
    this.$store.commit('forms/resetForm', {name: this.name})
  }

  public purge() {
    this.stopValidators()
    this.$store.commit('forms/delForm', {name: this.name})
  }

  public get errors() {
    if (this.purged) {
      return []
    }
    return this.attr('errors')
  }

  public get disabled(): boolean {
    return this.sending || this.attr('disabled')
  }

  public get sending(): boolean {
    return this.attr('sending')
  }

  public set sending(value: boolean) {
    // Not only used internally -- Sometimes useful when doing custom error handling.
    this.$store.commit('forms/updateMeta', {name: this.name, meta: {sending: value}})
  }

  public get bind() {
    return {errors: this.errors, sending: this.sending, id: `form-${this.name}`}
  }

  public get rawData(): RawData {
    return dataFromForm(this.$store.state.forms[this.name])
  }

  public get endpoint() {
    return this.attr('endpoint')
  }

  public set endpoint(endpoint) {
    this.$store.commit('forms/setEndpoint', {name: this.name, endpoint})
  }

  public get step() {
    return this.attr('step')
  }

  public set step(step: number) {
    this.$store.commit('forms/setStep', {name: this.name, step})
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

  public attr(attrName: keyof FormState): any {
    return this.$store.state.forms[this.name][attrName]
  }

  public clearErrors() {
    this.$store.commit('forms/clearErrors', {name: this.name})
  }

  public formWatch(mutation: MutationPayload) {
    if (this.watcherMap[mutation.type]) {
      this.watcherMap[mutation.type](mutation)
    }
  }

  public kill() {
    // no-op for compatibility
  }

  public watchAddField(mutation: MutationPayload) {
    if (mutation.payload.name !== this.name) {
      return
    }
    Vue.set(
      this.fields,
      mutation.payload.field.name,
      new FieldController(
        {store: this.$store, propsData: {formName: this.name, fieldName: mutation.payload.field.name}})
    )
  }

  public watchDelField(mutation: MutationPayload) {
    if (mutation.payload.name !== this.name) {
      return
    }
    Vue.delete(this.fields, mutation.payload.field)
    formRegistry.delete(this.name)
  }

  public watchDelForm(mutation: MutationPayload) {
    if (mutation.payload.name !== this.name) {
      return
    }
    this.fields = {}
    this.unsubscribe()
    formRegistry.delete(this.name)
  }

  public scrollToError() {
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

  public setErrors(error: AxiosError) {
    this.stopValidators()
    const errorSet = deriveErrors(error, Object.keys(this.fields))
    if (errorSet.errors.length && !Object.keys(errorSet.fields).length) {
      this.$store.commit(
        'forms/setMetaErrors',
        {name: this.name, errors: errorSet.errors})
      this.sending = false
      return
    }
    this.$store.commit('forms/setErrors', {name: this.name, errors: errorSet})
    this.sending = false
    this.$nextTick(this.scrollToError)
    return error
  }
}
