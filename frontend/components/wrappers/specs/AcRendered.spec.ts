import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'
import Vuetify from 'vuetify/lib'
import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import AcRendered from '../AcRendered'

describe('AcRendered.ts', () => {
  const localVue = vueSetup()
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  let vuetify: Vuetify
  beforeEach(() => {
    vuetify = createVuetify()
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Truncates text at a specific length', () => {
    wrapper = mount(AcRendered, {
      localVue,
      store,
      vuetify,
      propsData: {
        value: 'This is a section of text.', truncate: 10,
      },
    })
    expect(wrapper.text()).toBe('This is a... Read More')
  })
  it('Allows the user to read more', async() => {
    wrapper = mount(AcRendered, {
      localVue,
      store,
      vuetify,
      propsData: {
        value: 'This is a section of text.', truncate: 10,
      },
    })
    wrapper.find('.read-more-bar').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toBe('This is a section of text.')
  })
  it('Sets a default truncation level', async() => {
    wrapper = mount(AcRendered, {
      localVue,
      store,
      vuetify,
      propsData: {
        value: ''.padStart(1500, 'A'), truncate: true,
      },
    })
    expect(wrapper.text()).toBe(''.padStart(1000, 'A') + '... Read More')
  })
})
