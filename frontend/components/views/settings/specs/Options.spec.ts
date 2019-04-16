import Vue, {VueConstructor} from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import VueRouter from 'vue-router'
import {genUser} from '@/specs/helpers/fixtures'
import {setViewer, vuetifySetup} from '@/specs/helpers'
import Options from '../Options.vue'
import {Singles} from '@/store/singles/registry'
import {Profiles} from '@/store/profiles/registry'
import {Lists} from '@/store/lists/registry'

// Must use it directly, due to issues with package imports upstream.
Vue.use(Vuetify)
jest.useFakeTimers()

describe('Options.vue', () => {
  let store: ArtStore
  let localVue: VueConstructor
  let wrapper: Wrapper<Vue>
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(Singles)
    localVue.use(Lists)
    localVue.use(Profiles)
    store = createStore()
    vuetifySetup()
    if (wrapper) {
      wrapper.destroy()
    }
    localVue.use(VueRouter)
  })
  it('Mounts the options page', async() => {
    setViewer(store, genUser())
    wrapper = mount(Options, {
      localVue,
      store,
      propsData: {username: 'Fox'},
      attachToDocument: true,
      sync: false,
    })
    await wrapper.vm.$nextTick()
  })
  it('Generates the settings URL', async() => {
    setViewer(store, genUser())
    wrapper = mount(Options, {
      localVue,
      store,
      propsData: {username: 'Fox'},
      attachToDocument: true,
      sync: false,
    })
    expect((wrapper.vm as any).settingsUrl).toBe('/api/profiles/v1/account/Fox/')
  })
})
