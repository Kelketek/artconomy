import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {singleRegistry} from '@/store/singles/registry'
import {listRegistry} from '@/store/lists/registry'
import {mount, Wrapper} from '@vue/test-utils'
import {profileRegistry} from '@/store/profiles/registry'
import mockAxios from '@/__mocks__/axios'
import {characterRegistry} from '@/store/characters/registry'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {confirmAction, rq, rs, setViewer, vueSetup, vuetifySetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {formRegistry} from '@/store/forms/registry'
import {Character} from '@/store/characters/types/Character'
import AcCharacterToolbar from '@/components/views/character/AcCharacterToolbar.vue'

const localVue = vueSetup()

describe('AcCharacterToolbar.vue', () => {
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  let character: Character
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    singleRegistry.reset()
    listRegistry.reset()
    profileRegistry.reset()
    characterRegistry.reset()
    formRegistry.reset()
    mockAxios.reset()
    character = genCharacter()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    const mockResolve = jest.fn()
    mockResolve.mockImplementationOnce(() => ({href: '/target/url/'}))
    wrapper = mount(
      AcCharacterToolbar, {
        localVue,
        store,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {
          $route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}},
          $router: {resolve: mockResolve},
        },
        stubs: ['router-link'],
        sync: false,
        attachToDocument: true,
      })
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    vm.character.sharedWith.setList([])
    store.commit('characterModules/character__Fox__Kai/sharedWith/setReady', true)
    await vm.$nextTick()
  })
  it('Deletes a character', async() => {
    setViewer(store, genUser())
    const mockResolve = jest.fn()
    const mockReplace = jest.fn()
    mockResolve.mockImplementationOnce(() => ({href: '/target/url/'}))
    wrapper = mount(
      AcCharacterToolbar, {
        localVue,
        store,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {
          $route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}},
          $router: {resolve: mockResolve, replace: mockReplace},
        },
        stubs: ['router-link', 'ac-share-button'],
        sync: false,
        attachToDocument: true,
      })
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    await vm.$nextTick()
    mockAxios.reset()
    await confirmAction(wrapper, ['.delete-button'])
    expect(mockAxios.delete).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/characters/Kai/', 'delete')
    )
    mockAxios.mockResponse(rs(undefined))
    expect(mockReplace).toHaveBeenCalledWith({name: 'Profile', params: {username: 'Fox'}})
  })
})
