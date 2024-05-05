import {RouterLinkStub, VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, flushPromises, mount, rq, rs, vueSetup} from '@/specs/helpers/index.ts'
import {genUser, userResponse} from '@/specs/helpers/fixtures.ts'
import AcAvatar from '@/components/AcAvatar.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

let store: ArtStore
let wrapper: VueWrapper<any>

const mockError = vi.spyOn(console, 'error')

describe('AcAvatar', () => {
  beforeEach(() => {
    store = createStore()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Populates via username', async() => {
    const wrapper = mount(AcAvatar, {
      ...vueSetup({
        store,
        stubs: {RouterLink: RouterLinkStub},
      }),
      props: {username: 'Fox'},
    })
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/account/Fox/', 'get'))
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
    expect(wrapper.findComponent(RouterLinkStub).exists()).toBeFalsy()
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.profileLink).toEqual({
      name: 'AboutUser',
      params: {username: 'Fox'},
    })
    expect((wrapper.find('img').attributes().src)).toBe(
      'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
    )
  })
  test('Populates via ID remotely', async() => {
    const wrapper = mount(AcAvatar, {
      ...vueSetup({
        store,
        stubs: {RouterLink: RouterLinkStub},
      }),
      props: {userId: 1},
    })
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/data/user/id/1/', 'get', undefined, {}))
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.profileLink).toEqual({
      name: 'AboutUser',
      params: {username: 'Fox'},
    })
    expect((wrapper.find('img').attributes().src)).toBe(
      'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
    )
  })
  test('Populates via ID locally', async() => {
    setViewer(store, genUser())
    const wrapper = mount(AcAvatar, {
      ...vueSetup({
        store,
        stubs: {RouterLink: RouterLinkStub},
      }),
      props: {userId: 1},
    })
    expect(mockAxios.request).not.toHaveBeenCalled()
    const vm = wrapper.vm as any
    expect(vm.profileLink).toEqual({
      name: 'AboutUser',
      params: {username: 'Fox'},
    })
    expect((wrapper.find('img').attributes().src)).toBe(
      'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
    )
  })
  test('Logs an error if it has insufficient information', async() => {
    mockError.mockImplementation(() => undefined)
    wrapper = mount(AcAvatar, {
    ...vueSetup({
        store,
        stubs: {RouterLink: RouterLinkStub},
      }),
    })
    expect(mockError).toBeCalledWith('No username, no ID. We cannot load an avatar.')
  })
  test('Ignores a username update if the value is false', async() => {
    setViewer(store, genUser())
    const wrapper = mount(AcAvatar, {
      ...vueSetup({
        store,
        stubs: {RouterLink: RouterLinkStub},
      }),
      props: {username: 'Fox'},
    })
    wrapper.setProps({username: ''})
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.profileLink).toEqual({
      name: 'AboutUser',
      params: {username: 'Fox'},
    })
  })
  test('Repopulates if the username changes', async() => {
    setViewer(store, genUser())
    const wrapper = mount(AcAvatar, {
      ...vueSetup({
        store,
        stubs: {RouterLink: RouterLinkStub},
      }),
      props: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
    expect(mockAxios.request).not.toHaveBeenCalled()
    wrapper.setProps({username: 'Vulpes'})
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/account/Vulpes/', 'get'))
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
    const vulpes = genUser()
    vulpes.username = 'Vulpes'
    vulpes.avatar_url = '/static/stuff.jpg/'
    mockAxios.mockResponseFor({url: '/api/profiles/account/Vulpes/'}, rs(vulpes))
    await flushPromises()
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.profileLink).toEqual({
      name: 'AboutUser',
      params: {username: 'Vulpes'},
    })
    expect((wrapper.find('img').attributes().src)).toBe(
      '/static/stuff.jpg/',
    )
  })
  test('Bootstraps straight from a user', async() => {
    setViewer(store, genUser())
    const wrapper = mount(AcAvatar, {
      ...vueSetup({
        store,
        stubs: {RouterLink: RouterLinkStub},
      }),
      props: {user: genUser()},
    })
    await wrapper.vm.$nextTick()
    expect(mockAxios.request).not.toHaveBeenCalled()
    const vm = wrapper.vm as any
    expect(vm.profileLink).toEqual({
      name: 'AboutUser',
      params: {username: 'Fox'},
    })
    expect((wrapper.find('img').attributes().src)).toBe(
      'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
    )
  })
  test('Handles a guest account', async() => {
    const user = genUser()
    user.guest = true
    user.username = '__6'
    setViewer(store, genUser())
    const wrapper = mount(AcAvatar, {
      ...vueSetup({
        store,
        stubs: {RouterLink: RouterLinkStub},
      }),
      props: {user},
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.profileLink).toBeNull()
  })
  test('Does not produce a link when told not to.', async() => {
    const user = genUser()
    user.artist_mode = false
    setViewer(store, user)
    const wrapper = mount(AcAvatar, {
      ...vueSetup({
        store,
        stubs: {RouterLink: RouterLinkStub},
      }),
      props: {
        user,
        noLink: true,
      },
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.profileLink).toBe(null)
  })
})
