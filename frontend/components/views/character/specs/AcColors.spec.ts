import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {ArtStore, createStore} from '@/store'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {listRegistry, Lists} from '@/store/lists/registry'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import mockAxios from '@/__mocks__/axios'
import {characterRegistry, Characters} from '@/store/characters/registry'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import {setViewer, vuetifySetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import AcColors from '@/components/views/character/AcColors.vue'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import {Character} from '@/store/characters/types/Character'

Vue.use(Vuetify)
Vue.use(Vuex)
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)
localVue.use(Characters)
localVue.use(FormControllers)

describe('AcColors.vue', () => {
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
  it('Mounts a color display', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcColors, {
        localVue,
        store,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {$route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}}},
        stubs: ['router-link'],
        sync: false,
      })
    const vm = wrapper.vm as any
    const colors = []
    for (let index = 0; index < 7; index++) {
      const submission = genSubmission()
      colors.push({id: index, color: '#FFFFFF', note: `color${index}`})
    }
    vm.character.profile.setX(character)
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    vm.character.colors.setList(colors)
    store.commit('characterModules/character__Fox__Kai/colors/setReady', true)
    await vm.$nextTick()
  })
  it('Dynamically sets a color style', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcColors, {
        localVue,
        store,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {$route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}}},
        stubs: ['router-link'],
        sync: false,
      })
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    vm.character.colors.setList([])
    store.commit('characterModules/character__Fox__Kai/colors/setReady', true)
    vm.newColor.fields.color.update('#FFFFFF')
    await vm.$nextTick()
    expect(vm.newColorStyle).toEqual({'background-color': '#FFFFFF'})
  })
})
