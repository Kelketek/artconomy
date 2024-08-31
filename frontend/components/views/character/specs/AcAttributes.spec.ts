import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import mockAxios from '@/__mocks__/axios.ts'
import {genCharacter} from '@/store/characters/specs/fixtures.ts'
import {cleanUp, flushPromises, mount, rs, vueSetup} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {Character} from '@/store/characters/types/Character.ts'
import AcAttributes from '@/components/views/character/AcAttributes.vue'
import {describe, expect, beforeEach, afterEach, test} from 'vitest'
import {setViewer} from '@/lib/lib.ts'
import {nextTick} from 'vue'

describe('AcAttributes.vue', () => {
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
  test('Mounts an attribute listing', async() => {
    setViewer({ store, user: genUser() })
    wrapper = mount(
      AcAttributes, {
        ...vueSetup({
          store,
        }),
        props: {
          username: 'Fox',
          characterName: 'Kai',
        },
      })
    const vm = wrapper.vm as any
    const attributes = []
    for (let index = 0; index < 7; index++) {
      attributes.push({
        id: index,
        sticky: index < 3,
        key: `key${index}`,
        value: `value${index}`,
      })
    }
    vm.character.profile.setX(character)
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    vm.character.attributes.setList(attributes)
    store.commit('characterModules/character__Fox__Kai/attributes/setReady', true)
    await nextTick()
  })
  test('Handles a new attribute', async() => {
    setViewer({ store, user: genUser() })
    wrapper = mount(
      AcAttributes, {
        ...vueSetup({
          store,
        }),
        props: {
          username: 'Fox',
          characterName: 'Kai',
        },
      })
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    store.commit('characterModules/character__Fox__Kai/profile/setFetching', false)
    store.commit('characterModules/character__Fox__Kai/attributes/setReady', true)
    store.commit('characterModules/character__Fox__Kai/attributes/setFetching', false)
    await nextTick()
    vm.addAttribute({
      id: 1,
      sticky: false,
      key: 'Stuff',
      value: 'things',
    })
    await nextTick()
    await nextTick()
    expect(vm.character.attributes.list[0].x).toEqual({
      id: 1,
      sticky: false,
      key: 'Stuff',
      value: 'things',
    })
  })
  test('Updates the tags on the character', async() => {
    setViewer({ store, user: genUser() })
    wrapper = mount(
      AcAttributes, {
        ...vueSetup({
          store,
        }),
        props: {
          username: 'Fox',
          characterName: 'Kai',
        },
      })
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    vm.character.profile.ready = true
    vm.character.profile.fetching = false
    vm.character.attributes.ready = true
    vm.character.attributes.fetching = true
    mockAxios.reset()
    await nextTick()
    vm.character.attributes.setList([{
      key: 'Species',
      value: 'Foxie',
      sticky: true,
    }])
    await nextTick()
    const request = mockAxios.lastReqGet()
    expect(request.url).toBe('/api/profiles/account/Fox/characters/Kai/')
    const updatedCharacter = genCharacter()
    updatedCharacter.name = 'Wat'
    updatedCharacter.tags = ['hello', 'there']
    mockAxios.mockResponse(rs(updatedCharacter))
    await flushPromises()
    await nextTick()
    const localCharacter = vm.character.profile.x as Character
    expect(localCharacter.tags).toEqual(['hello', 'there'])
    // We should only update the tags.
    expect(localCharacter.name).toBe('Kai')
  })
})
