import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {Vuetify} from 'vuetify'
import {ArtStore, createStore} from '@/store'
import {confirmAction, createVuetify, flushPromises, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import Router from 'vue-router'
import mockAxios from '@/__mocks__/axios'
import Journal from '@/components/views/Journal.vue'
import {genJournal} from '@/components/views/specs/fixtures'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('Journal.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
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
    mockAxios.reset()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts a journal', async() => {
    wrapper = mount(Journal, {
      localVue, store, router, vuetify, propsData: {journalId: 1, username: 'Fox'}, sync: false, attachToDocument: true}
    )
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/profiles/v1/account/Fox/journals/1/', 'get'))
    expect(wrapper.find('.edit-toggle').exists()).toBe(false)
    expect(wrapper.find('.delete-button').exists()).toBe(false)
  })
  it('Deletes a journal', async() => {
    router.push('/')
    setViewer(store, genUser())
    wrapper = mount(Journal, {
      localVue, store, router, vuetify, propsData: {journalId: 1, username: 'Fox'}, sync: false, attachToDocument: true}
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
