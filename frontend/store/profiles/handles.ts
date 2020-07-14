import Vue from 'vue'
import {User} from './types/User'

declare type handleDecorator = (cls: Vue, propName: string) => void

export function userHandle(
  source: string, setError?: boolean,
): handleDecorator {
  return (cls, propName) => {
    if (setError === undefined) {
      setError = true
    }
    Object.defineProperty(cls, propName, {
      get(): User | null {
        const self = (this as Vue)
        const propSource = (self as any)[source]
        if (propSource === null) {
          // Handler may not have yet been initialized. Can happen with some watchers.
          return null
        }
        if (!((typeof (self as any)[source] === 'object') && (!propSource.profile_handler__))) {
          console.warn(
            `Expected profile controller on property named '${source}', got `, propSource, ' instead.',
          )
          return null
        }
        return propSource.user.x
      },
    })
  }
}
