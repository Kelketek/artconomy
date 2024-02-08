import {formRegistry} from './registry.ts'
import cloneDeep from 'lodash/cloneDeep'
import debounce from 'lodash/debounce'
import axios from 'axios'
import deepEqual from 'fast-deep-equal'
import {ComputedGetters, dotTraverse, flatten} from '@/lib/lib.ts'
import {FormError} from '@/store/forms/types/FormError.ts'
import {FormState} from '@/store/forms/types/FormState.ts'
import {ValidatorSpec} from '@/store/forms/types/ValidatorSpec.ts'
import {RawData} from '@/store/forms/types/RawData.ts'
import {Field} from '@/store/forms/types/Field.ts'
import {ControllerArgs} from '@/store/controller-base.ts'
import {ArtStore} from '@/store/index.ts'
import {ComputedGetter, ref, toValue, watch} from 'vue'

export function axiosCatch(error: Error) {
  if (axios.isCancel(error)) {
    return []
  }
  console.trace(error)
  return []
}

declare interface FieldControllerArgs extends Omit<ControllerArgs<undefined>, "initName" | "schema" > {
  fieldName: string,
  formName: string,
}

@ComputedGetters
export class FieldController {
  public __getterMap: Map<keyof FieldController, ComputedGetter<any>>
  public fieldName: string
  public formName: string
  public $store: ArtStore
  public validate!: ReturnType<typeof debounce>
  public cancelSource = new AbortController()
  public localCache: any = ref(null)

  constructor({fieldName, formName, $store}: FieldControllerArgs) {
    // Used by the ComputedGetters decorator
    this.__getterMap = new Map()
    this.fieldName = fieldName
    this.formName = formName
    this.$store = $store
    this.validate = debounce(
      this.runValidation, this.debounceRate, {trailing: true},
    )
    // Force creation of the value computed getter.
    this.value
    watch(this.__getterMap.get('value'), this.syncCache, {immediate: true})
    watch(this.localCache, this.updateInternal, {deep: true})
  }

  public get value () {
    return this.attr('value')
  }

  public get errors() {
    return this.attr('errors')
  }

  public get step() {
    return this.attr('step')
  }

  public get model() {
    return toValue(this.localCache)
  }

  public set model(value) {
    this.update(value)
  }

  public get initialData() {
    return this.attr('initialData')
  }

  public set initialData(value: any) {
    const data: RawData = {}
    data[this.fieldName] = cloneDeep(value)
    this.$store.commit('forms/updateInitialData', {name: this.formName, data})
  }

  // Watcher for value
  public syncCache = (val: any)=> {
    if (val === undefined) {
      // Should not happen unless we're tearing down.
      return
    }
    this.localCache.value = cloneDeep(val)
  }

  // Watcher for localCache
  public updateInternal = (newVal: any) => {
    /* istanbul ignore if */
    if (newVal === undefined) {
      // Should not happen unless we're tearing down.
      return
    }
    // Ensure that the store is updated even if we've had to clone out a copy and save that.
    if (deepEqual(this.value, newVal)) {
      return
    }
    this.update(newVal)
  }

  public get id() {
    const sourceString = `field-${flatten(this.formName)}__${flatten(this.fieldName)}`
    let destString = ''
    for (const char of sourceString) {
      if (/[a-zA-Z0-9_-]/.test(char)) {
        destString += char
      } else {
        destString += CSS.escape(char)
      }
    }
    return destString
  }

  public get rawBind() {
    // For fields which are raw html fields, like the input tag.
    return {
      // Native elements use value
      value: this.value,
      disabled: this.attr('disabled') || this.formAttr('sending'),
      id: this.id,
      onBlur: this.forceValidate,
      onInput: this.domUpdate,
      onChange: this.domUpdate,
      ...this.attr('extra'),
    }
  }

  public get bind() {
    // Downstream wrapper will need to remove irrelevant entries.
    return {
      modelValue: this.value,
      errorMessages: this.errors,
      disabled: this.attr('disabled') || this.formAttr('sending'),
      id: this.id,
      onBlur: this.forceValidate,
      'onUpdate:modelValue': this.update,
      ...this.attr('extra'),
    }
  }

  public forceValidate = () => {
    // Calls the debounced validator, then forcibly flushes it, making sure we don't screw up the debounce handling if
    // we need to validate immediately.
    this.validate()
    this.validate.flush()
  }

  public cancelValidation = () => {
    this.validate.cancel()
    this.cancelSource.abort()
    this.cancelSource = new AbortController()
  }

  public kill = () => {
    // no-op for compatibility
  }

  public get debounceRate() {
    if (this.attr('debounce') !== null) {
      return this.attr('debounce')
    }
    return this.$store.state.forms![this.formName]!.debounce
  }

  public get form() {
    // DO NOT use getform from within this controller or the fields will get registered in the form's reference counter.
    // This will prevent them from ever being reaped!
    return formRegistry.controllers[this.formName]
  }

  public attr = (attrName: keyof Field): any => {
    return dotTraverse(
      this, `$store.state.forms.${this.formName}.fields.${this.fieldName}.${attrName}`, true,
    )
  }

  public formAttr = (attrName: keyof FormState): any => {
    return this.$store.state.forms![this.formName][attrName]
  }

  public get validators() {
    return this.attr('validators')
  }

  public domUpdate = (event: InputEvent) => {
    this.update((event.target as HTMLInputElement).value)
  }

  public update = (value: any, validate: boolean = true) => {
    const data: RawData = {}
    data[this.fieldName] = cloneDeep(value)
    this.$store.commit('forms/updateValues', {name: this.formName, data})
    if (validate) {
      this.validate()
    }
  }

  private runValidation = ()=> {
    const errors: string[] = []
    const allValidators = this.attr('validators')
    const syncValidators = allValidators.filter((validator: ValidatorSpec) => !validator.async)
    // Run our syncronous validators first.
    for (const validator of syncValidators) {
      if (!formRegistry.validators[validator.name]) {
        console.error(
          'Unregistered synchronous validator: ', validator.name, '\n', 'Options are: ',
          Object.keys(formRegistry.validators))
        continue
      }
      errors.push(...formRegistry.validators[validator.name](this, ...(validator.args || [])))
    }
    const errorFields: FormError = {}
    errorFields[this.fieldName] = errors
    const asyncValidators = allValidators.filter((validator: ValidatorSpec) => validator.async)
    const promiseSet: Array<Promise<any>> = []
    // Run the async validators
    for (const validator of asyncValidators) {
      if (!formRegistry.asyncValidators[validator.name]) {
        console.error(
          'Unregistered asynchronous validator: ', validator.name, '\n', 'Options are: ',
          Object.keys(formRegistry.asyncValidators))
        continue
      }
      const args = cloneDeep(validator.args || [])
      args.unshift(this.cancelSource.signal)
      promiseSet.push(
        formRegistry.asyncValidators[validator.name](this, ...args).catch(axiosCatch),
      )
    }
    // Batch up the results of all validators to avoid having the form error messages bounce back and forth between
    // valid and invalid.
    Promise.all(promiseSet).then((results: string[][]) => {
      for (const result of results) {
        errors.push(...result)
      }
      this.$store.commit('forms/setFieldErrors', {name: this.formName, fields: errorFields})
    })
  }

  public toJSON = () => {
    // Used to prevent the pretty printing service from exhausting all memory.
    return {type: this.constructor.name, name: this.fieldName, state: this.value}
  }
}
