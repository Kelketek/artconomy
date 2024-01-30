// Sets up a convenience computed property for getting all the registries at once. Should be installed after all the
// other modules.

import {createApp, markRaw} from 'vue'
import {RegistryRegistry} from '@/store/registry-base'
import {singleRegistry} from '@/store/singles/registry'
import {listRegistry} from '@/store/lists/registry'
import {formRegistry} from '@/store/forms/registry'
import {characterRegistry} from '@/store/characters/registry'
import {profileRegistry} from '@/store/profiles/registry'


export const buildRegistries = () => markRaw({
  Single: singleRegistry,
  List: listRegistry,
  Form: formRegistry,
  Character: characterRegistry,
  Profile: profileRegistry,
})


export const createRegistries = () => {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin({
        computed: {
          $registries(): RegistryRegistry {
            return buildRegistries()
          }
        }
      })
    }
  }
}
