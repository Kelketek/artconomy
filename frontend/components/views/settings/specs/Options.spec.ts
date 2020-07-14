import Vue from 'vue'
import {Vuetify} from 'vuetify/types'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import VueRouter from 'vue-router'
import {genUser} from '@/specs/helpers/fixtures'
import {createVuetify, docTarget, setViewer, vueSetup} from '@/specs/helpers'
import Options from '../Options.vue'

jest.useFakeTimers()

describe('Options.vue', () => {
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  let vuetify: Vuetify
  const localVue = vueSetup()
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    localVue.use(VueRouter)
  })
  it('Mounts the options page', async() => {
    setViewer(store, genUser())
    wrapper = mount(Options, {
      localVue,
      store,
      vuetify,
      propsData: {username: 'Fox'},
      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
  })
  it('Generates the settings URL', async() => {
    setViewer(store, genUser())
    wrapper = mount(Options, {
      localVue,
      store,
      vuetify,
      propsData: {username: 'Fox'},
      attachTo: docTarget(),
    })
    expect((wrapper.vm as any).settingsUrl).toBe('/api/profiles/v1/account/Fox/')
  })
})
