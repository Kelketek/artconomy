import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {ArtStore, createStore} from '@/store'
import {confirmAction, flushPromises, rq, rs, setViewer, vuetifySetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {listRegistry, Lists} from '@/store/lists/registry'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import Router from 'vue-router'
import mockAxios from '@/__mocks__/axios'
import Journal from '@/components/views/Journal.vue'
import {genJournal} from '@/components/views/specs/fixtures'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)
localVue.use(FormControllers)
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router

describe('Journal.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = new Router({mode: 'history',
      routes: [{
        path: '/',
        name: 'Home',
        component: Empty,
      }, {
        path: '/:username/',
        name: 'Profile',
        component: Empty,
        children: [
          {path: 'products', name: 'Products', component: Empty},
        ],
      }, {
        path: '/login/',
        name: 'Login',
        component: Empty,
      },
      ]})
    singleRegistry.reset()
    listRegistry.reset()
    formRegistry.reset()
    profileRegistry.reset()
    vuetifySetup()
    mockAxios.reset()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts a journal', async() => {
    wrapper = mount(Journal, {
      localVue, store, router, propsData: {journalId: 1, username: 'Fox'}, sync: false, attachToDocument: true}
    )
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/profiles/v1/account/Fox/journals/1/', 'get'))
    expect(wrapper.find('.edit-toggle').exists()).toBe(false)
    expect(wrapper.find('.delete-button').exists()).toBe(false)
  })
  it('Deletes a journal', async() => {
    router.push('/')
    setViewer(store, genUser())
    wrapper = mount(Journal, {
      localVue, store, router, propsData: {journalId: 1, username: 'Fox'}, sync: false, attachToDocument: true}
    )
    mockAxios.mockResponse(rs(genJournal()))
    // Comments
    mockAxios.mockResponse(rs({count: 0, size: 5, results: []}))
    await wrapper.vm.$nextTick()
    const toggle = wrapper.find('.edit-toggle')
    expect(toggle.exists()).toBe(true)
    toggle.trigger('click')
    await wrapper.vm.$nextTick()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    expect(mockAxios.delete).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/journals/1/', 'delete')
    )
    mockAxios.mockResponse(rs(null))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.path).toBe('/Fox')
  })
})
