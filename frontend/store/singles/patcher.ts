// Patcher that allows more flexibility in defining how data will be sent. In most cases, you want patcher in the
// singles module instead.
import Vue from 'vue'
import {artCall, dotTraverse} from '@/lib/lib'
import {debounce, cloneDeep} from 'lodash'
import axios, {AxiosError, CancelTokenSource} from 'axios'
import {deriveErrors} from '@/store/forms/helpers'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import {SingleController} from '@/store/singles/controller'

declare type patcherDecorator = (cls: Vue, propName: string) => void

declare interface PatchConfig {
  dirty: boolean,
  cancelSource: CancelTokenSource,
  cached: any,
  errors: string[],
  debouncedSet: (val: any) => void,
  silent?: boolean,
  patching: boolean,
}

export function errorSend(config: Patch): (error: AxiosError) => void {
  return (error: AxiosError) => {
    const attrName = config.attrName
    if (axios.isCancel(error)) {
      // We recalled the request deliberately. This is not an error, so ignore. Also, this should only happen when
      // sending a new request, so don't reset the patching flag.
      return
    }
    const errors = deriveErrors(error, [attrName])
    const message = (errors.fields[attrName] && errors.fields[attrName][0]) || errors.errors[0]
    config.errors = [message]
    config.patching = false
  }
}

@Component
export class Patch extends Vue {
  @Prop({required: true})
  public target!: any

  @Prop({required: true})
  public modelProp!: string

  @Prop({required: true})
  public attrName!: string

  @Prop({default: 250})
  public debounceRate!: number

  // Used for automaticly generated patchers which may throw errors during initialization/dereference
  @Prop({default: false})
  public silent!: boolean

  @Prop({default: true})
  public refresh!: boolean

  public cancelSource = axios.CancelToken.source()
  public forceRecompute = 0
  public errors: string[] = []
  public dirty = false
  public cached = null
  public patching = false
  public loaded = false

  public rawSet(val: any) {
    let handler: SingleController<any>
    if (!this.modelProp) {
      handler = this.target
    } else {
      handler = dotTraverse(this.target, this.modelProp, true) || {}
    }
    const model = handler.x || {}
    const oldVal = model[this.attrName]
    if (oldVal === undefined) {
      console.error(Error(`Cannot set undefined key on model: ${this.attrName}`))
      return undefined
    }
    const data: { [key: string]: any } = {}
    data[this.attrName] = val
    this.cancelSource.cancel()
    this.cancelSource = axios.CancelToken.source()
    this.errors = []
    this.patching = true
    if (handler.endpoint === '#') {
      // This is an a special case where we're just using the single as scaffolding for Vuex storage.
      handler.updateX(data)
      return
    }
    artCall({
      url: handler.endpoint,
      method: 'patch',
      data,
      cancelToken: this.cancelSource.token,
    },
    ).then(
      (response) => {
        handler.updateX(response)
        if (!this.refresh) {
          this.dirty = false
        }
        this.patching = false
      },
    ).catch(errorSend(this))
  }

  public setValue(val: any) {
    // Broken out into its own function so we can force retry as needed.
    this.cached = val
    if (this.cached === this.rawValue) {
      this.dirty = false
      return
    }
    this.dirty = true
    // eslint-disable-next-line no-useless-call
    this.debouncedSet.apply(this, [val])
  }

  public get handler(): any {
    // Needed to make this a separate handler in order to make sure recomputation is always triggered in patch fields
    // when the raw X value is replaced by setX.
    let handler: SingleController<any>
    if (!this.modelProp) {
      handler = this.target
    } else {
      handler = dotTraverse(this.target, this.modelProp, true) || {}
    }
    return handler
  }

  public get rawValue(): any {
    const handler = this.handler
    const model = handler.x
    // Believe it or not, typeof null is 'object'.
    if ((typeof model !== 'object') || model === null) {
      /* istanbul ignore else */
      if (!this.silent) {
        console.warn(
          `Expected object in property named '${this.modelProp}', got `, model, ' instead.',
        )
      }
      this.loaded = false
      return undefined
    }
    if (model[this.attrName] === undefined) {
      /* istanbul ignore else */
      if (!this.silent) {
        console.error(`"${this.attrName}" is undefined on model "${this.modelProp}"`)
      }
      this.loaded = false
      return undefined
    }
    const value = model[this.attrName]
    if (typeof value === 'object') {
      this.loaded = true
      return cloneDeep(value)
    }
    this.loaded = true
    return model[this.attrName]
  }

  public get model() {
    if (this.dirty) {
      return this.cached
    }
    return this.rawValue
  }

  public set model(val) {
    this.setValue(val)
  }

  public get debouncedSet() {
    return debounce(this.rawSet, this.debounceRate, {trailing: true})
  }
}

export interface PatcherConfig {
  modelProp: string
  attrName: string
  debounceRate?: number,
  refresh?: boolean,
  silent?: boolean,
}
