import { ArtStore, createStore } from "@/store/index.ts"
import { VueWrapper } from "@vue/test-utils"
import { genCharacter } from "@/store/characters/specs/fixtures.ts"
import { cleanUp, mount, vueSetup } from "@/specs/helpers/index.ts"
import { genUser } from "@/specs/helpers/fixtures.ts"
import AcColors from "@/components/views/character/AcColors.vue"
import { describe, beforeEach, afterEach, test } from "vitest"
import { setViewer } from "@/lib/lib.ts"
import { Character } from "@/store/characters/types/main"

describe("AcColors.vue", () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  let character: Character
  beforeEach(() => {
    store = createStore()
    character = genCharacter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Mounts a color display", async () => {
    setViewer({ store, user: genUser() })
    wrapper = mount(AcColors, {
      ...vueSetup({
        store,
        mocks: {
          $route: {
            name: "Character",
            params: {
              username: "Fox",
              characterName: "Kai",
            },
            query: {},
          },
        },
        stubs: ["router-link"],
      }),
      props: {
        username: "Fox",
        characterName: "Kai",
      },
    })
    const vm = wrapper.vm as any
    const colors = []
    for (let index = 0; index < 7; index++) {
      colors.push({
        id: index,
        color: "#FFFFFF",
        note: `color${index}`,
      })
    }
    vm.character.profile.setX(character)
    store.commit("characterModules/character__Fox__Kai/profile/setReady", true)
    vm.character.colors.setList(colors)
    store.commit("characterModules/character__Fox__Kai/colors/setReady", true)
    await vm.$nextTick()
  })
})
