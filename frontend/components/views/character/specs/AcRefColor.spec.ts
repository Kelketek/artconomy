import Vue from 'vue'
import {Vuetify} from 'vuetify'
import {mount, Wrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ArtStore, createStore} from '@/store'
import AcRefColor from '@/components/views/character/AcRefColor.vue'
import {cleanUp, createVuetify, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()

describe('AcRefColor.vue', () => {
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  let vuetify: Vuetify
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, {localVue, store, sync: false})
    const color = empty.vm.$getSingle('color', {endpoint: '/endpoint/'})
    color.setX({color: '#555555', note: 'This is a test color'})
    wrapper = mount(AcRefColor, {
      propsData: {color, username: 'Fox'},
      localVue,
      store,
      vuetify,
      sync: false,
      mocks: {
        $route: {name: 'Character', params: {}, query: {}},
      },
    })
  })
  it('Launches a color picker', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, {localVue, store, sync: false})
    const color = empty.vm.$getSingle('color', {endpoint: '/endpoint/'})
    color.setX({color: '#555555', note: 'This is a test color'})
    wrapper = mount(AcRefColor, {
      propsData: {color, username: 'Fox'},
      localVue,
      store,
      vuetify,
      sync: false,
      mocks: {
        $route: {name: 'Character', params: {}, query: {}},
      },
    })
    const mockClick = jest.spyOn(wrapper.find('.picker').element, 'click')
    wrapper.find('.picker-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockClick).toHaveBeenCalled()
  })
})
