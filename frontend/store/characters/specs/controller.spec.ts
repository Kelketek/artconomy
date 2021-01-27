import {genUser} from '@/specs/helpers/fixtures'
import {cleanUp, setViewer, vueSetup, mount} from '@/specs/helpers'
import {Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import Vue, {VueConstructor} from 'vue'
import mockAxios from '@/specs/helpers/mock-axios'
import {CharacterController} from '@/store/characters/controller'
import {genCharacter} from '@/store/characters/specs/fixtures'

describe('Profile controller', () => {
  let store: ArtStore
  let localVue: VueConstructor
  let wrapper: Wrapper<Vue> | null
  beforeEach(() => {
    mockAxios.reset()
    localVue = vueSetup()
    store = createStore()
    wrapper = null
  })
  afterEach(() => {
    cleanUp(wrapper || undefined)
  })
  it('Updates the route if the character name changed', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = jest.fn()
    wrapper = mount(CharacterController, {
      localVue,
      store,
      propsData: {initName: 'Fox:Kai', schema: {username: 'Fox', characterName: 'Kai'}},
      mocks: {
        $route: {
          name: 'Place', params: {username: 'Fox', characterName: 'Kai'}, query: {stuff: 'things'}, hash: 'Wheee',
        },
        $router: {replace},
      },

    })
    const vm = wrapper.vm as any
    vm.profile.setX(genCharacter())
    await wrapper.vm.$nextTick();
    (wrapper.vm as any).profile.updateX({name: 'Zorro'})
    await wrapper.vm.$nextTick()
    expect(replace).toHaveBeenCalled()
    expect(replace).toHaveBeenCalledWith({
      name: 'Place', params: {username: 'Fox', characterName: 'Zorro'}, query: {stuff: 'things'}, hash: 'Wheee',
    },
    )
  })
  it('Leaves the route alone if no username is in it.', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = jest.fn()
    wrapper = mount(CharacterController, {
      localVue,
      store,
      propsData: {initName: 'Fox:Kai', schema: {username: 'Fox', characterName: 'Kai'}},
      mocks: {
        $route: {
          name: 'Place', params: {characterName: 'Kai'}, query: {stuff: 'things'}, hash: 'Wheee',
        },
        $router: {replace},
      },

    })
    const vm = wrapper.vm as any
    vm.profile.setX(genCharacter())
    await wrapper.vm.$nextTick();
    (wrapper.vm as any).profile.updateX({name: 'Zorro'})
    await wrapper.vm.$nextTick()
    expect(replace).not.toHaveBeenCalled()
  })
  it('Leaves the route alone if no character name in it.', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = jest.fn()
    wrapper = mount(CharacterController, {
      localVue,
      store,
      propsData: {initName: 'Fox:Kai', schema: {username: 'Fox', characterName: 'Kai'}},
      mocks: {
        $route: {
          name: 'Place', params: {username: 'Fox'}, query: {stuff: 'things'}, hash: 'Wheee',
        },
        $router: {replace},
      },

    })
    const vm = wrapper.vm as any
    vm.profile.setX(genCharacter())
    await wrapper.vm.$nextTick();
    (wrapper.vm as any).profile.updateX({name: 'Zorro'})
    await wrapper.vm.$nextTick()
    expect(replace).not.toHaveBeenCalled()
  })
  it('Leaves the route alone if a different character name is in it.', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = jest.fn()
    wrapper = mount(CharacterController, {
      localVue,
      store,
      propsData: {initName: 'Fox:Kai', schema: {username: 'Fox', characterName: 'Kai'}},
      mocks: {
        $route: {
          name: 'Place', params: {username: 'Fox', characterName: 'Fern'}, query: {stuff: 'things'}, hash: 'Wheee',
        },
        $router: {replace},
      },

    })
    const vm = wrapper.vm as any
    vm.profile.setX(genCharacter())
    await wrapper.vm.$nextTick();
    (wrapper.vm as any).profile.updateX({name: 'Zorro'})
    await wrapper.vm.$nextTick()
    expect(replace).not.toHaveBeenCalled()
  })
  it('Leaves the route alone if a different username is present', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = jest.fn()
    wrapper = mount(CharacterController, {
      localVue,
      store,
      propsData: {initName: 'Fox:Kai', schema: {username: 'Fox', characterName: 'Kai'}},
      mocks: {
        $route: {
          name: 'Place', params: {username: 'Bob', characterName: 'Kai'}, query: {stuff: 'things'}, hash: 'Wheee',
        },
        $router: {replace},
      },

    })
    const vm = wrapper.vm as any
    vm.profile.setX(genCharacter())
    await wrapper.vm.$nextTick();
    (wrapper.vm as any).profile.updateX({name: 'Zorro'})
    await wrapper.vm.$nextTick()
    expect(replace).not.toHaveBeenCalled()
  })
})
