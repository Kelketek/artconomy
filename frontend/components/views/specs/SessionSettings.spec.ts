import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, genAnon, qMount, setViewer, vueSetup} from '@/specs/helpers'
import {Wrapper} from '@vue/test-utils'
import SessionSettings from '@/components/views/SessionSettings.vue'
import {genUser} from '@/specs/helpers/fixtures'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('SessionSettings.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts a settings panel for an anonymous user', async() => {
    setViewer(store, genAnon())
    wrapper = qMount(SessionSettings, {localVue, store, stubs: ['router-link']})
  })
  it('Redirects a registered user', async() => {
    setViewer(store, genUser())
    const replace = jest.fn()
    wrapper = qMount(SessionSettings, {localVue, store, mocks: {$router: {replace}}, stubs: ['router-link']})
    await wrapper.vm.$nextTick()
    expect(replace).toHaveBeenCalledWith({name: 'Settings', params: {username: 'Fox'}})
  })
  it('Conditionally permits the rating to be adjusted per session', async() => {
    setViewer(store, genAnon({birthday: null}))
    wrapper = qMount(SessionSettings, {
      localVue,
      store,
      stubs: ['router-link'],
    })
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
})
