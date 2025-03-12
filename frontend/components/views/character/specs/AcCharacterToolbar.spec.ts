import { ArtStore, createStore } from "@/store/index.ts"
import { VueWrapper } from "@vue/test-utils"
import mockAxios from "@/__mocks__/axios.ts"
import { genCharacter } from "@/store/characters/specs/fixtures.ts"
import {
  cleanUp,
  confirmAction,
  createTestRouter,
  mount,
  rq,
  rs,
  vueSetup,
  waitFor,
} from "@/specs/helpers/index.ts"
import { genUser } from "@/specs/helpers/fixtures.ts"
import AcCharacterToolbar from "@/components/views/character/AcCharacterToolbar.vue"
import { describe, expect, beforeEach, afterEach, test, vi } from "vitest"
import { setViewer } from "@/lib/lib.ts"
import { nextTick } from "vue"
import { Character } from "@/store/characters/types/main"

describe("AcCharacterToolbar.vue", () => {
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
  test("Mounts", async () => {
    setViewer({ store, user: genUser() })
    const mockResolve = vi.fn()
    mockResolve.mockImplementation(() => ({ href: "/target/url/" }))
    wrapper = mount(AcCharacterToolbar, {
      ...vueSetup({
        store,
      }),
      props: {
        username: "Fox",
        characterName: "Kai",
      },
    })
    wrapper.vm.character.profile.setX(character)
    store.commit("characterModules/character__Fox__Kai/profile/setReady", true)
    wrapper.vm.character.sharedWith.setList([])
    store.commit(
      "characterModules/character__Fox__Kai/sharedWith/setReady",
      true,
    )
    await wrapper.vm.$nextTick()
  })
  test("Deletes a character", async () => {
    setViewer({ store, user: genUser() })
    const router = createTestRouter()
    await router.push({
      name: "Character",
      params: { username: "Fox", characterName: "Kai" },
    })
    wrapper = mount(AcCharacterToolbar, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        username: "Fox",
        characterName: "Kai",
      },
    })
    wrapper.vm.character.profile.setX(character)
    store.commit("characterModules/character__Fox__Kai/profile/setReady", true)
    await wrapper.vm.$nextTick()
    mockAxios.reset()
    await confirmAction(wrapper, [".more-button", ".delete-button"])
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq("/api/profiles/account/Fox/characters/Kai/", "delete"),
    )
    mockAxios.mockResponse(rs(undefined))
    await waitFor(() =>
      expect(router.currentRoute.value.name).toEqual("Profile"),
    )
    await waitFor(() =>
      expect(router.currentRoute.value.params.username).toEqual("Fox"),
    )
  })
  test("Determines which asset to share", async () => {
    setViewer({ store, user: genUser() })
    const mockResolve = vi.fn()
    mockResolve.mockImplementation(() => ({ href: "/target/url/" }))
    wrapper = mount(AcCharacterToolbar, {
      ...vueSetup({
        store,
      }),
      props: {
        username: "Fox",
        characterName: "Kai",
      },
    })
    const character = genCharacter()
    wrapper.vm.character.profile.setX(character)
    await nextTick()
    expect(wrapper.vm.shareMedia).toBeTruthy()
    expect(wrapper.vm.shareMedia).toEqual(character.primary_submission)
  })
  test("Handles a character with no primary asset", async () => {
    setViewer({ store, user: genUser() })
    const mockResolve = vi.fn()
    mockResolve.mockImplementation(() => ({ href: "/target/url/" }))
    wrapper = mount(AcCharacterToolbar, {
      ...vueSetup({
        store,
      }),
      props: {
        username: "Fox",
        characterName: "Kai",
      },
    })
    const character = genCharacter({ primary_submission: null })
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    expect(vm.shareMedia).toBeNull()
  })
  test("Handles an upload properly", async () => {
    setViewer({ store, user: genUser() })
    const mockResolve = vi.fn()
    mockResolve.mockImplementation(() => ({ href: "/target/url/" }))
    wrapper = mount(AcCharacterToolbar, {
      ...vueSetup({
        store,
      }),
      props: {
        username: "Fox",
        characterName: "Kai",
      },
    })
    const character = genCharacter({ primary_submission: null })
    wrapper.vm.character.profile.makeReady(character)
    await nextTick()
    expect(wrapper.vm.showUpload).toBe(false)
    await wrapper.find(".upload-button").trigger("click")
    await nextTick()
    expect(wrapper.vm.showUpload).toBe(true)
    await waitFor(() => expect(wrapper.vm.submissionDialog).toBeTruthy())
    wrapper.vm.submissionDialog.$emit("success", "test")
    expect(wrapper.vm.showUpload).toBe(false)
    await nextTick()
  })
})
