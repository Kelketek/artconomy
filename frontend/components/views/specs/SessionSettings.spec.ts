import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, genAnon, setViewer, vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import SessionSettings from '@/components/views/SessionSettings.vue'
import {genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('SessionSettings.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts a settings panel for an anonymous user', async() => {
    setViewer(store, genAnon())
    wrapper = mount(SessionSettings, {
      localVue, store, sync: false, attachToDocument: true, stubs: ['router-link']})
  })
  it('Redirects a registered user', async() => {
    setViewer(store, genUser())
    const replace = jest.fn()
    wrapper = mount(SessionSettings, {
      localVue, store, sync: false, attachToDocument: true, mocks: {$router: {replace}}, stubs: ['router-link']})
    await wrapper.vm.$nextTick()
    expect(replace).toHaveBeenCalledWith({name: 'Settings', params: {username: 'Fox'}})
  })
})
