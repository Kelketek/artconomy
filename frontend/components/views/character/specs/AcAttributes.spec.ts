import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import mockAxios from '@/__mocks__/axios'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {cleanUp, createVuetify, docTarget, flushPromises, rs, setViewer, vueSetup, mount} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {Character} from '@/store/characters/types/Character'
import AcAttributes from '@/components/views/character/AcAttributes.vue'

const localVue = vueSetup()

describe('AcAttributes.vue', () => {
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
  it('Mounts an attribute listing', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcAttributes, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {$route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}}},
        stubs: ['router-link'],

        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
    const attributes = []
    for (let index = 0; index < 7; index++) {
      attributes.push({id: index, sticky: index < 3, key: `key${index}`, value: `value${index}`})
    }
    vm.character.profile.setX(character)
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    vm.character.attributes.setList(attributes)
    store.commit('characterModules/character__Fox__Kai/attributes/setReady', true)
    await vm.$nextTick()
  })
  it('Handles a new attribute', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcAttributes, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {$route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {editing: 'true'}}},
        stubs: ['router-link'],

        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    store.commit('characterModules/character__Fox__Kai/profile/setFetching', false)
    store.commit('characterModules/character__Fox__Kai/attributes/setReady', true)
    store.commit('characterModules/character__Fox__Kai/attributes/setFetching', false)
    await vm.$nextTick()
    vm.addAttribute({id: 1, sticky: false, key: 'Stuff', value: 'things'})
    await vm.$nextTick()
    await vm.$nextTick()
    expect(vm.character.attributes.list[0].x).toEqual({id: 1, sticky: false, key: 'Stuff', value: 'things'})
  })
  it('Updates the tags on the character', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcAttributes, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {$route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {editing: 'true'}}},
        stubs: ['router-link'],

        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    vm.character.profile.ready = true
    vm.character.profile.fetching = false
    vm.character.attributes.ready = true
    vm.character.attributes.fetching = true
    mockAxios.reset()
    await vm.$nextTick()
    vm.character.attributes.setList([{key: 'Species', value: 'Foxie', sticky: true}])
    await vm.$nextTick()
    const request = mockAxios.lastReqGet()
    expect(request.url).toBe('/api/profiles/account/Fox/characters/Kai/')
    const updatedCharacter = genCharacter()
    updatedCharacter.name = 'Wat'
    updatedCharacter.tags = ['hello', 'there']
    mockAxios.mockResponse(rs(updatedCharacter))
    await flushPromises()
    await vm.$nextTick()
    const localCharacter = vm.character.profile.x as Character
    expect(localCharacter.tags).toEqual(['hello', 'there'])
    // We should only update the tags.
    expect(localCharacter.name).toBe('Kai')
  })
})
