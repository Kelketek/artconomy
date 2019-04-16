import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ArtStore, createStore} from '@/store'
import {Singles} from '@/store/singles/registry'
import AcRefColor from '@/components/views/character/AcRefColor.vue'
import {setViewer, vuetifySetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {Profiles} from '@/store/profiles/registry'
import {Lists} from '@/store/lists/registry'

Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)

describe('AcRefColor.vue', () => {
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  beforeEach(() => {
    store = createStore()
    vuetifySetup()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
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
