import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import mockAxios from '@/__mocks__/axios.ts'
import {genCharacter} from '@/store/characters/specs/fixtures.ts'
import {
  cleanUp,
  confirmAction,
  mount,
  rq,
  rs,
  vueSetup,
  VuetifyWrapped, waitFor,
} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {Character} from '@/store/characters/types/Character.ts'
import AcCharacterToolbar from '@/components/views/character/AcCharacterToolbar.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import flushPromises from 'flush-promises'
import {setViewer} from '@/lib/lib.ts'

const WrappedToolbar = VuetifyWrapped(AcCharacterToolbar)

describe('AcCharacterToolbar.vue', () => {
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
  test('Mounts', async() => {
    setViewer(store, genUser())
    const mockResolve = vi.fn()
    mockResolve.mockImplementation(() => ({href: '/target/url/'}))
    wrapper = mount(
      WrappedToolbar, {
        ...vueSetup({
          store,
          mocks: {
            $route: {
              name: 'Character',
              params: {
                username: 'Fox',
                characterName: 'Kai',
              },
              query: {},
            },
            $router: {resolve: mockResolve},
          },
          stubs: ['router-link'],
        }),
        props: {
          username: 'Fox',
          characterName: 'Kai',
        },
      })
    const vm = wrapper.vm.$refs.vm as any
    vm.character.profile.setX(character)
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    vm.character.sharedWith.setList([])
    store.commit('characterModules/character__Fox__Kai/sharedWith/setReady', true)
    await vm.$nextTick()
  })
  test('Deletes a character', async() => {
    setViewer(store, genUser())
    const mockResolve = vi.fn()
    const mockReplace = vi.fn()
    mockResolve.mockImplementation(() => ({href: '/target/url/'}))
    wrapper = mount(
      WrappedToolbar, {
        ...vueSetup({
          store,
          mocks: {
            $route: {
              name: 'Character',
              params: {
                username: 'Fox',
                characterName: 'Kai',
              },
              query: {},
            },
            $router: {
              resolve: mockResolve,
              replace: mockReplace,
            },
          },
          stubs: ['router-link', 'ac-share-button'],
        }),
        props: {
          username: 'Fox',
          characterName: 'Kai',
        },
      })
    const vm = wrapper.vm.$refs.vm as any
    vm.character.profile.setX(character)
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    await vm.$nextTick()
    mockAxios.reset()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Fox/characters/Kai/', 'delete'),
    )
    mockAxios.mockResponse(rs(undefined))
    await vm.$nextTick()
    await flushPromises()
    expect(mockReplace).toHaveBeenCalledWith({
      name: 'Profile',
      params: {username: 'Fox'},
    })
  })
  test('Determines which asset to share', async() => {
    setViewer(store, genUser())
    const mockResolve = vi.fn()
    mockResolve.mockImplementation(() => ({href: '/target/url/'}))
    wrapper = mount(
      AcCharacterToolbar, {
        ...vueSetup({
          store,
          mocks: {
            $route: {
              name: 'Character',
              params: {
                username: 'Fox',
                characterName: 'Kai',
              },
              query: {},
            },
            $router: {resolve: mockResolve},
          },
          stubs: ['router-link'],
        }),
        props: {
          username: 'Fox',
          characterName: 'Kai',
        },
      })
    const character = genCharacter()
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    await vm.$nextTick()
    expect(vm.shareMedia).toBeTruthy()
    expect(vm.shareMedia).toEqual(character.primary_submission)
  })
  test('Handles a character with no primary asset', async() => {
    setViewer(store, genUser())
    const mockResolve = vi.fn()
    mockResolve.mockImplementation(() => ({href: '/target/url/'}))
    wrapper = mount(
      AcCharacterToolbar, {
        ...vueSetup({
          store,
          mocks: {
            $route: {
              name: 'Character',
              params: {
                username: 'Fox',
                characterName: 'Kai',
              },
              query: {},
            },
            $router: {resolve: mockResolve},
          },
          stubs: ['router-link'],
        }),
        props: {
          username: 'Fox',
          characterName: 'Kai',
        },
      })
    const character = genCharacter({primary_submission: null})
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    expect(vm.shareMedia).toBeNull()
  })
  test('Handles an upload properly', async() => {
    setViewer(store, genUser())
    const mockResolve = vi.fn()
    mockResolve.mockImplementation(() => ({href: '/target/url/'}))
    wrapper = mount(
      WrappedToolbar, {
        ...vueSetup({
          store,
          mocks: {
            $route: {
              name: 'Character',
              params: {
                username: 'Fox',
                characterName: 'Kai',
              },
              query: {},
            },
            $router: {resolve: mockResolve},
          },
          stubs: ['router-link'],
        }),
        props: {
          username: 'Fox',
          characterName: 'Kai',
        },
      })
    const character = genCharacter({primary_submission: null})
    const vm = wrapper.vm.$refs.vm as any
    vm.character.profile.makeReady(character)
    await vm.$nextTick()
    expect(vm.showUpload).toBe(false)
    await wrapper.find('.upload-button').trigger('click')
    await vm.$nextTick()
    expect(vm.showUpload).toBe(true)
    await waitFor(() => expect(vm.$refs.submissionDialog).toBeTruthy())
    vm.$refs.submissionDialog.$emit('success', 'test')
    expect(vm.showUpload).toBe(false)
    await vm.$nextTick()
  })
})
