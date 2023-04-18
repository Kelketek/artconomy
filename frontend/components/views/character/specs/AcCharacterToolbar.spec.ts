import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import mockAxios from '@/__mocks__/axios'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {cleanUp, confirmAction, createVuetify, docTarget, rq, rs, setViewer, vueSetup, mount} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {Character} from '@/store/characters/types/Character'
import AcCharacterToolbar from '@/components/views/character/AcCharacterToolbar.vue'

const localVue = vueSetup()

describe('AcCharacterToolbar.vue', () => {
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  let character: Character
  let vuetify: Vuetify
  beforeEach(() => {
    store = createStore()
    character = genCharacter()
    vuetify = createVuetify()
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
        vuetify,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {
          $route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}},
          $router: {resolve: mockResolve},
        },
        stubs: ['router-link'],
        attachTo: docTarget(),
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
        vuetify,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {
          $route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}},
          $router: {resolve: mockResolve, replace: mockReplace},
        },
        stubs: ['router-link', 'ac-share-button'],

        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
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
    expect(mockReplace).toHaveBeenCalledWith({name: 'Profile', params: {username: 'Fox'}})
  })
  it('Determines which asset to share', async() => {
    setViewer(store, genUser())
    const mockResolve = jest.fn()
    mockResolve.mockImplementation(() => ({href: '/target/url/'}))
    wrapper = mount(
      AcCharacterToolbar, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {
          $route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}},
          $router: {resolve: mockResolve},
        },
        stubs: ['router-link'],
        attachTo: docTarget(),
      })
    const character = genCharacter()
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    await vm.$nextTick()
    expect(vm.shareMedia).toBeTruthy()
    expect(vm.shareMedia).toEqual(character.primary_submission)
  })
  it('Handles a character with no primary asset', async() => {
    setViewer(store, genUser())
    const mockResolve = jest.fn()
    mockResolve.mockImplementation(() => ({href: '/target/url/'}))
    wrapper = mount(
      AcCharacterToolbar, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {
          $route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}},
          $router: {resolve: mockResolve},
        },
        stubs: ['router-link'],
        attachTo: docTarget(),
      })
    const character = genCharacter({primary_submission: null})
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    expect(vm.shareMedia).toBeNull()
  })
  it('Handles an upload properly', async() => {
    setViewer(store, genUser())
    const mockResolve = jest.fn()
    mockResolve.mockImplementation(() => ({href: '/target/url/'}))
    wrapper = mount(
      AcCharacterToolbar, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {
          $route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}},
          $router: {resolve: mockResolve},
        },
        stubs: ['router-link'],
        attachTo: docTarget(),
      })
    const character = genCharacter({primary_submission: null})
    const vm = wrapper.vm as any
    vm.character.profile.makeReady(character)
    await vm.$nextTick()
    expect(vm.showUpload).toBe(false)
    wrapper.find('.upload-button').trigger('click')
    await vm.$nextTick()
    expect(vm.showUpload).toBe(true)
    wrapper.find('.submission-uploader').vm.$emit('success', 'test')
    expect(vm.showUpload).toBe(false)
    expect(wrapper.emitted().success).toBeTruthy()
    expect(wrapper.emitted().success![0]).toEqual(['test'])
  })
})
