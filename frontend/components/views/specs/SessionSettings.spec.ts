import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import SessionSettings from '@/components/views/SessionSettings.vue'
import {genAnon, genUser} from '@/specs/helpers/fixtures.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('SessionSettings.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts a settings panel for an anonymous user', async() => {
    setViewer(store, genAnon())
    wrapper = mount(SessionSettings, vueSetup({
      store,
      stubs: ['router-link'],
    }))
  })
  test('Redirects a registered user', async() => {
    setViewer(store, genUser())
    const replace = vi.fn()
    wrapper = mount(SessionSettings, vueSetup({
      store,
      mocks: {$router: {replace}},
      stubs: ['router-link'],
    }))
    await wrapper.vm.$nextTick()
    expect(replace).toHaveBeenCalledWith({
      name: 'Settings',
      params: {username: 'Fox'},
    })
  })
  test('Conditionally permits the rating to be adjusted per session', async() => {
    setViewer(store, genAnon({birthday: null}))
    wrapper = mount(SessionSettings, vueSetup({
      store,
      stubs: ['router-link'],
    }))
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.adultAllowed).toBe(false)
    vm.viewerHandler.user.updateX({birthday: '1988-08-01'})
    await vm.$nextTick()
    expect(vm.adultAllowed).toBe(true)
    vm.viewerHandler.user.updateX({sfw_mode: true})
    await vm.$nextTick()
    expect(vm.adultAllowed).toBe(false)
  })
  test('Reopens the cookie dialog', async() => {
    setViewer(store, genAnon({birthday: null}))
    wrapper = mount(SessionSettings, vueSetup({
      store,
      stubs: ['router-link'],
    }))
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(store.state.showCookieDialog).toBe(false)
    wrapper.find('.cookie-settings-button').trigger('click')
    await vm.$nextTick()
    expect(store.state.showCookieDialog).toBe(true)
  })
})
