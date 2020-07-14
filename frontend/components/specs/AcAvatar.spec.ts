import Vue from 'vue'
import {mount, RouterLinkStub, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, flushPromises, rq, rs, setViewer, vueSetup, vuetifySetup} from '@/specs/helpers'
import {genUser, userResponse} from '@/specs/helpers/fixtures'
import AcAvatar from '@/components/AcAvatar.vue'
import mockAxios from '@/__mocks__/axios'
import {Vuetify} from 'vuetify/types'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

const mockError = jest.spyOn(console, 'error')

describe('Avatar', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Populates via username', async() => {
    const wrapper = mount(AcAvatar, {
      localVue,
      store,
      vuetify,
      propsData: {username: 'Fox'},
      stubs: {RouterLink: RouterLinkStub},
    })
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/profiles/v1/account/Fox/', 'get'))
    expect(mockAxios.get).toHaveBeenCalledTimes(1)
    expect(wrapper.findComponent(RouterLinkStub).exists()).toBeFalsy()
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    expect(wrapper.findComponent(RouterLinkStub).props().to).toEqual({name: 'Products', params: {username: 'Fox'}})
    expect((wrapper.find('img').attributes().src)).toBe(
      'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
    )
  })
  it('Populates via ID remotely', async() => {
    const wrapper = mount(AcAvatar, {
      localVue,
      store,
      vuetify,
      propsData: {userId: 1},
      stubs: {RouterLink: RouterLinkStub},

    })
    expect(mockAxios.get).toHaveBeenCalledTimes(1)
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/profiles/v1/data/user/id/1/', 'get', undefined, {}))
    expect(wrapper.findComponent(RouterLinkStub).exists()).toBeFalsy()
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(wrapper.findComponent(RouterLinkStub).props().to).toEqual({name: 'Products', params: {username: 'Fox'}})
    expect((wrapper.find('img').attributes().src)).toBe(
      'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
    )
  })
  it('Populates via ID locally', async() => {
    setViewer(store, genUser())
    const wrapper = mount(AcAvatar, {
      localVue,
      store,
      vuetify,
      propsData: {userId: 1},
      stubs: {RouterLink: RouterLinkStub},

    })
    expect(mockAxios.get).not.toHaveBeenCalled()
    expect(wrapper.findComponent(RouterLinkStub).props().to).toEqual({name: 'Products', params: {username: 'Fox'}})
    expect((wrapper.find('img').attributes().src)).toBe(
      'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
    )
  })
  it('Throws an error if it has insufficient information', async() => {
    mockError.mockImplementation(() => undefined)
    expect(() => {
      mount(AcAvatar, {
        localVue,
        store,
        vuetify,
        stubs: {RouterLink: RouterLinkStub},

      })
    }).toThrow(Error('No username, no ID. We cannot load an avatar.'))
  })
  it('Ignores a username update if the value is false', async() => {
    setViewer(store, genUser())
    const wrapper = mount(AcAvatar, {
      localVue, store, propsData: {username: 'Fox'}, stubs: {RouterLink: RouterLinkStub},
    })
    wrapper.setProps({username: ''})
    await wrapper.vm.$nextTick()
    expect(wrapper.findComponent(RouterLinkStub).props().to).toEqual({name: 'Products', params: {username: 'Fox'}})
  })
  it('Repopulates if the username changes', async() => {
    setViewer(store, genUser())
    const wrapper = mount(AcAvatar, {
      localVue,
      store,
      vuetify,
      propsData: {username: 'Fox'},
      stubs: {RouterLink: RouterLinkStub},
    })
    await wrapper.vm.$nextTick()
    expect(mockAxios.get).not.toHaveBeenCalled()
    wrapper.setProps({username: 'Vulpes'})
    await wrapper.vm.$nextTick()
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/profiles/v1/account/Vulpes/', 'get'))
    expect(mockAxios.get).toHaveBeenCalledTimes(1)
    const vulpes = genUser()
    vulpes.username = 'Vulpes'
    vulpes.avatar_url = '/static/stuff.jpg/'
    mockAxios.mockResponse(rs(vulpes))
    await wrapper.vm.$nextTick()
    expect(wrapper.findComponent(RouterLinkStub).props().to).toEqual({name: 'Products', params: {username: 'Vulpes'}})
    expect((wrapper.find('img').attributes().src)).toBe(
      '/static/stuff.jpg/',
    )
  })
  it('Bootstraps straight from a user', async() => {
    setViewer(store, genUser())
    const wrapper = mount(AcAvatar, {
      localVue,
      store,
      vuetify,
      propsData: {user: genUser()},
      stubs: {RouterLink: RouterLinkStub},
    })
    await wrapper.vm.$nextTick()
    expect(mockAxios.get).not.toHaveBeenCalled()
    expect(wrapper.findComponent(RouterLinkStub).props().to).toEqual({name: 'Products', params: {username: 'Fox'}})
    expect((wrapper.find('img').attributes().src)).toBe(
      'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
    )
  })
  it('Sends to about tab if not an artist', async() => {
    const user = genUser()
    user.artist_mode = false
    setViewer(store, user)
    const wrapper = mount(AcAvatar, {
      localVue,
      store,
      vuetify,
      propsData: {user},
      stubs: {RouterLink: RouterLinkStub},

    })
    await wrapper.vm.$nextTick()
    expect(mockAxios.get).not.toHaveBeenCalled()
    expect(wrapper.findComponent(RouterLinkStub).props().to).toEqual({name: 'AboutUser', params: {username: 'Fox'}})
    expect((wrapper.find('img').attributes().src)).toBe(
      'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
    )
  })
  it('Handles a guest account', async() => {
    const user = genUser()
    user.guest = true
    user.username = '__6'
    setViewer(store, genUser())
    const wrapper = mount(AcAvatar, {
      localVue,
      store,
      vuetify,
      propsData: {user},
      stubs: {RouterLink: RouterLinkStub},

    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.profileLink).toBeNull()
  })
  it('Does not produce a link when told not to.', async() => {
    const user = genUser()
    user.artist_mode = false
    setViewer(store, user)
    const wrapper = mount(AcAvatar, {
      localVue,
      store,
      vuetify,
      propsData: {user, noLink: true},
      stubs: {RouterLink: RouterLinkStub},
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.profileLink).toBe(null)
  })
})
