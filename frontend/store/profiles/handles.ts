import {User} from './types/User.ts'
import {ArtVueInterface} from '@/types/ArtVueInterface.ts'
import {ArtVue} from '@/lib/lib.ts'

declare type handleDecorator = (cls: InstanceType<typeof ArtVue>, propName: string) => void

export function userHandle(
  source: string, setError?: boolean,
): handleDecorator {
  return (cls: InstanceType<typeof ArtVue>, propName) => {
    if (setError === undefined) {
      setError = true
    }
    Object.defineProperty(cls, propName, {
      get(): User | null {
        const self = (this as ArtVueInterface)
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
