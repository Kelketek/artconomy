import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {genCharacter} from '@/store/characters/specs/fixtures.ts'
import {cleanUp, createVuetify, mount, setViewer, vueSetup} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import AcColors from '@/components/views/character/AcColors.vue'
import {Character} from '@/store/characters/types/Character.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

describe('AcColors.vue', () => {
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
  test('Mounts a color display', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcColors, {
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
          },
          stubs: ['router-link'],
        }),
        props: {
          username: 'Fox',
          characterName: 'Kai',
        },
      })
    const vm = wrapper.vm as any
    const colors = []
    for (let index = 0; index < 7; index++) {
      colors.push({
        id: index,
        color: '#FFFFFF',
        note: `color${index}`,
      })
    }
    vm.character.profile.setX(character)
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    vm.character.colors.setList(colors)
    store.commit('characterModules/character__Fox__Kai/colors/setReady', true)
    await vm.$nextTick()
  })
  test('Dynamically sets a color style', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcColors, {
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
          },
          stubs: ['router-link'],
        }),
        props: {
          username: 'Fox',
          characterName: 'Kai',
        },
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
