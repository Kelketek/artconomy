import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import {cleanUp, createVuetify, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import AcColors from '@/components/views/character/AcColors.vue'
import {Character} from '@/store/characters/types/Character'
import {Vuetify} from 'vuetify/types'

const localVue = vueSetup()
let vuetify: Vuetify

describe('AcColors.vue', () => {
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  let character: Character
  beforeEach(() => {
    store = createStore()
    character = genCharacter()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts a color display', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcColors, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {$route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}}},
        stubs: ['router-link'],

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
        vuetify,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {$route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}}},
        stubs: ['router-link'],

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
