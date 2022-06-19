import Vue from 'vue'
import {formRegistry} from './registry'
import Component from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'
import cloneDeep from 'lodash/cloneDeep'
import debounce from 'lodash/debounce'
import axios, {CancelTokenSource} from 'axios'
import deepEqual from 'fast-deep-equal'
import {dotTraverse, flatten} from '@/lib/lib'
import {FormError} from '@/store/forms/types/FormError'
import {FormState} from '@/store/forms/types/FormState'
import {ValidatorSpec} from '@/store/forms/types/ValidatorSpec'
import {RawData} from '@/store/forms/types/RawData'
import {Field} from '@/store/forms/types/Field'

export function axiosCatch(error: Error) {
  if (axios.isCancel(error)) {
    return []
  }
  console.trace(error)
  return []
}

@Component
export class FieldController extends Vue {
  // Manages the state of a field. Useful for plugging into forms.
  @Prop()
  public fieldName!: string

  @Prop()
  public formName!: string

  public validate!: ReturnType<typeof debounce>
  public cancelSource: CancelTokenSource = axios.CancelToken.source()
  public localCache: any = null

  public get value() {
    return this.attr('value')
  }

  public get errors() {
    return this.attr('errors')
  }

  public get step() {
    return this.attr('step')
  }

  public get model() {
    return this.localCache
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

  @Watch('value', {immediate: true})
  public syncCache(val: any) {
    if (val === undefined) {
      // Should not happen unless we're tearing down.
      return
    }
    Vue.set(this, 'localCache', cloneDeep(val))
  }

  @Watch('localCache', {deep: true})
  public updateInternal(newVal: any) {
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
    return `field-${flatten(this.formName)}__${flatten(this.fieldName)}`
  }

  public get bind() {
    return {
      // Checkboxes use inputValue due to naming conflicts with the native DOM.
      value: this.value,
      inputValue: this.value,
      errorMessages: this.errors,
      disabled: this.attr('disabled') || this.formAttr('sending'),
      id: this.id,
      ...this.attr('extra'),
    }
  }

  public created() {
    this.validate = debounce(
      this.runValidation, this.debounceRate, {trailing: true},
    )
  }

  public forceValidate() {
    // Calls the debounced validator, then forcibly flushes it, making sure we don't screw up the debounce handling if
    // we need to validate immediately.
    this.validate()
    this.validate.flush()
  }

  public cancelValidation() {
    this.validate.cancel()
    this.cancelSource.cancel()
    this.cancelSource = axios.CancelToken.source()
  }

  public kill() {
    // no-op for compatibility
  }

  public get on() {
    return {change: this.update, input: this.update, blur: this.forceValidate}
  }

  public get debounceRate() {
    if (this.attr('debounce') !== null) {
      return this.attr('debounce')
    }
    return this.$store.state.forms[this.formName].debounce
  }

  public get form() {
    // DO NOT use getform from within this controller or the fields will get registered in the form's reference counter.
    // This will prevent them from ever being reaped!
    return formRegistry.controllers[this.formName]
  }

  public attr(attrName: keyof Field): any {
    const form = this.$store.state.forms[this.formName]
    return dotTraverse(
      this, `$store.state.forms.${this.formName}.fields.${this.fieldName}.${attrName}`, true,
    )
  }

  public formAttr(attrName: keyof FormState): any {
    return this.$store.state.forms[this.formName][attrName]
  }

  public get validators() {
    return this.attr('validators')
  }

  public update(value: any, validate?: boolean) {
    if (validate === undefined) {
      validate = true
    }
    const data: RawData = {}
    data[this.fieldName] = cloneDeep(value)
    this.$store.commit('forms/updateValues', {name: this.formName, data})
    if (validate) {
      this.validate()
    }
  }

  private runValidation() {
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
      args.unshift(this.cancelSource.token)
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

  public toJSON() {
    // Used to prevent the pretty printing service from exhausting all memory.
    return {type: this.constructor.name, name: this.fieldName, state: this.value}
  }
}
