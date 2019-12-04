import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import mockAxios from '@/__mocks__/axios'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {cleanUp, confirmAction, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {Character} from '@/store/characters/types/Character'
import AcCharacterToolbar from '@/components/views/character/AcCharacterToolbar.vue'

const localVue = vueSetup()

describe('AcCharacterToolbar.vue', () => {
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  let character: Character
  beforeEach(() => {
    store = createStore()
    character = genCharacter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    const mockResolve = jest.fn()
    mockResolve.mockImplementation(() => ({href: '/target/url/'}))
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
    mockResolve.mockImplementation(() => ({href: '/target/url/'}))
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
