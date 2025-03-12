// Sets up a convenience computed property for getting all the registries at once. Should be installed after all the
// other modules.

import { createApp, markRaw } from "vue"
import { registryKey, RegistryRegistry } from "@/store/registry-base.ts"
import { singleRegistry } from "@/store/singles/registry.ts"
import { listRegistry } from "@/store/lists/registry.ts"
import { formRegistry } from "@/store/forms/registry.ts"
import { characterRegistry } from "@/store/characters/registry.ts"
import { profileRegistry } from "@/store/profiles/registry.ts"

export const buildRegistries = () =>
  markRaw({
    Single: singleRegistry,
    List: listRegistry,
    Form: formRegistry,
    Character: characterRegistry,
    Profile: profileRegistry,
  })

export const createRegistries = () => {
  return {
    install(app: ReturnType<typeof createApp>) {
      const registries = buildRegistries()
      app.mixin({
        computed: {
          $registries(): RegistryRegistry {
            return registries
          },
        },
      })
      app.provide(registryKey, registries)
    },
  }
}
