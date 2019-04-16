import {vuetifySetup} from '@/specs/helpers'
import Vuetify from 'vuetify'
import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {Singles} from '@/store/singles/registry'
import {Profiles} from '@/store/profiles/registry'
import AcRendered from '../AcRendered'

Vue.use(Vuetify)
Vue.use(Vuex)

describe('AcRendered.ts', () => {
  const localVue = createLocalVue()
  localVue.use(Singles)
  localVue.use(Profiles)
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Truncates text at a specific length', () => {
    wrapper = mount(AcRendered, {localVue,
      store,
      propsData: {
        value: 'This is a section of text.', truncate: 10,
      }})
    expect(wrapper.text()).toBe('This is a... Read More')
  })
  it('Allows the user to read more', async() => {
    wrapper = mount(AcRendered, {localVue,
      store,
      propsData: {
        value: 'This is a section of text.', truncate: 10, sync: false,
      }})
    wrapper.find('.read-more-bar').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toBe('This is a section of text.')
  })
  it('Sets a default truncation level', async() => {
    wrapper = mount(AcRendered, {localVue,
      store,
      propsData: {
        value: ''.padStart(1500, 'A'), truncate: true, sync: false,
      }})
    expect(wrapper.text()).toBe(''.padStart(1000, 'A') + '... Read More')
  })
})
