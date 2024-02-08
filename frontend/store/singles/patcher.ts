// Patcher that allows more flexibility in defining how data will be sent. In most cases, you want patcher in the
// singles module instead.
import {artCall, ComputedGetters, dotTraverse} from '@/lib/lib.ts'
import cloneDeep from 'lodash/cloneDeep'
import debounce from 'lodash/debounce'
import axios, {AxiosError} from 'axios'
import {deriveErrors} from '@/store/forms/helpers.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {ComputedGetter, ref, Ref, toValue} from 'vue'
import {v4 as uuidv4} from 'uuid'

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
    config.errors.value = [message]
    config.patching.value = false
  }
}

export interface PatcherArgs {
  target: any,
  modelProp: string,
  attrName: string,
  debounceRate?: number,
  silent?: boolean,
  refresh?: boolean
}

const uncached = Symbol('Uncached')

@ComputedGetters
export class Patch<T = any> {
  public __getterMap: Map<keyof Patch, ComputedGetter<any>>
  public target!: any
  public modelProp: string
  public attrName: string
  public debounceRate: number
  public _uid: string
  // Used for automatically generated patchers which may throw errors during initialization/dereference
  public silent: boolean
  public refresh: boolean

  constructor(args: PatcherArgs) {
    this.__getterMap = new Map()
    this.target  = args.target
    this.modelProp = args.modelProp
    this.attrName = args.attrName
    this.debounceRate = args.debounceRate || 250
    this.silent = args.silent || false
    this.refresh = args.refresh === undefined ? true : args.refresh
    this._uid = uuidv4()
  }

  public cancelSource = new AbortController()
  public errors = ref([] as string[])
  public cached: Ref<Symbol|T> = ref(uncached)
  public patching = ref(false)

  public rawSet = (val: T) => {
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
    this.cancelSource.abort()
    this.cancelSource = new AbortController()
    this.errors.value = []
    if (handler.endpoint === '#') {
      // This is a special case where we're just using the single as scaffolding for Vuex storage.
      handler.updateX(data)
      return
    }
    this.patching.value = true
    artCall({
      url: handler.endpoint,
      method: 'patch',
      data,
      signal: this.cancelSource.signal,
    },
    ).then(
      (response) => {
        handler.updateX(response)
        this.patching.value = false
        if (this.cached.value === this.rawValue) {
          this.cached.value = uncached
        }
      },
    ).catch((err) => {
      errorSend(this)(err)
    })
  }

  public setValue = (val: T) => {
    val = toValue(val)
    // Broken out into its own function so that we can force retry as needed.
    this.cached.value = toValue(val)
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

  public get loaded(): boolean {
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
      return false
    }
    if (model[this.attrName] === undefined) {
      /* istanbul ignore else */
      if (!this.silent) {
        console.error(`"${this.attrName}" is undefined on model "${this.modelProp}"`)
      }
      return false
    }
    return true
  }

  public get rawValue(): any {
    const handler = this.handler
    const model = handler.x
    if (!this.loaded) {
      return undefined
    }
    const value = model[this.attrName]
    if (typeof value === 'object') {
      return cloneDeep(value)
    }
    return model[this.attrName]
  }

  public get dirty() {
    // @ts-ignore
    const cached = toValue(this.cached)
    if (cached === uncached) {
      return false
    }
    return cached !== this.rawValue
  }

  public get model(): T {
    if (this.dirty) {
      return toValue(this.cached) as T
    }
    return toValue(this.rawValue)
  }

  public set model(val: T) {
    this.setValue(val)
  }

  public get debouncedSet() {
    return debounce(this.rawSet, this.debounceRate, {trailing: true})
  }
}

export interface PatcherConfig {
  target?: any,
  modelProp: string
  attrName: string
  debounceRate?: number,
  refresh?: boolean,
  silent?: boolean,
}
