import {genUser} from '@/specs/helpers/fixtures'
import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import mockAxios from '@/specs/helpers/mock-axios'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import Empty from '@/specs/helpers/dummy_components/empty'

describe('Profile controller', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    mockAxios.reset()
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Updates the route if the character name changed', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = vi.fn()
    wrapper = mount(Empty, {
      ...vueSetup({
        store,
        mocks: {
          $router: {
            replace,
            currentRoute: {
              name: 'Place',
              params: {
                username: 'Fox',
                characterName: 'Kai'
              },
              query: {stuff: 'things'},
              hash: 'Wheee',
            },
          },
        },
      }),
    })
    const controller = wrapper.vm.$getCharacter('Fox:Kai', {username: 'Fox', characterName: 'Kai'})
    controller.profile.setX(genCharacter())
    await wrapper.vm.$nextTick();
    controller.profile.updateX({name: 'Zorro'})
    await wrapper.vm.$nextTick()
    expect(replace).toHaveBeenCalled()
    expect(replace).toHaveBeenCalledWith({
      name: 'Place', params: {username: 'Fox', characterName: 'Zorro'}, query: {stuff: 'things'}, hash: 'Wheee',
    })
  })
  test('Leaves the route alone if no username is in it.', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = vi.fn()
    wrapper = mount(Empty, {
      ...vueSetup({
        store,
        mocks: {
          $router: {
            replace,
            currentRoute: {
              name: 'Place', params: {characterName: 'Kai'}, query: {stuff: 'things'}, hash: 'Wheee',
            },
          },
        },
      }),
    })
    const controller = wrapper.vm.$getCharacter('Fox:Kai', {username: 'Fox', characterName: 'Kai'})
    controller.profile.setX(genCharacter())
    await wrapper.vm.$nextTick();
    controller.profile.updateX({name: 'Zorro'})
    await wrapper.vm.$nextTick()
    expect(replace).not.toHaveBeenCalled()
  })
  test('Leaves the route alone if no character name in it.', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = vi.fn()
    wrapper = mount(Empty, {
      ...vueSetup({
        store,
        mocks: {
          $router: {
            replace,
            currentRoute: {
              name: 'Place', params: {username: 'Fox'}, query: {stuff: 'things'}, hash: 'Wheee',
            },
          },
        },
      }),
    })
    const controller = wrapper.vm.$getCharacter('Fox:Kai', {username: 'Fox', characterName: 'Kai'})
    controller.profile.setX(genCharacter())
    await wrapper.vm.$nextTick();
    controller.profile.updateX({name: 'Zorro'})
    await wrapper.vm.$nextTick()
    expect(replace).not.toHaveBeenCalled()
  })
  test('Leaves the route alone if a different character name is in it.', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = vi.fn()
    wrapper = mount(Empty, {
      ...vueSetup({
        store,
        mocks: {
          $route: {
            name: 'Place', params: {username: 'Fox', characterName: 'Fern'}, query: {stuff: 'things'}, hash: 'Wheee',
          },
          $router: {
            replace,
            currentRoute: {
              name: 'Place', params: {username: 'Fox', characterName: 'Fern'}, query: {stuff: 'things'}, hash: 'Wheee',
            },
          },
        },
      }),
    })
    const controller = wrapper.vm.$getCharacter('Fox:Kai', {username: 'Fox', characterName: 'Kai'})
    controller.profile.setX(genCharacter())
    await wrapper.vm.$nextTick();
    controller.profile.updateX({name: 'Zorro'})
    await wrapper.vm.$nextTick()
    expect(replace).not.toHaveBeenCalled()
  })
  test('Leaves the route alone if a different username is present', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = vi.fn()
    wrapper = mount(Empty, {
      ...vueSetup({
        store,
        mocks: {
          $router: {
            replace,
            currentRoute: {
              name: 'Place', params: {username: 'Bob', characterName: 'Kai'}, query: {stuff: 'things'}, hash: 'Wheee',
            },
          },
        },
      }),
    })
    const controller = wrapper.vm.$getCharacter('Fox:Kai', {username: 'Fox', characterName: 'Kai'})
    controller.profile.setX(genCharacter())
    await wrapper.vm.$nextTick();
    controller.profile.updateX({name: 'Zorro'})
    await wrapper.vm.$nextTick()
    expect(replace).not.toHaveBeenCalled()
  })
})
