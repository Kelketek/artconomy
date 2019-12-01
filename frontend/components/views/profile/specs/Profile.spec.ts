import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {ArtStore, createStore} from '@/store'
import {flushPromises, rq, rs, setViewer, vuetifySetup} from '@/specs/helpers'
import {genArtistProfile, genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {listRegistry, Lists} from '@/store/lists/registry'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import Router from 'vue-router'
import mockAxios from '@/__mocks__/axios'
import {genConversation} from '@/components/views/specs/fixtures'
import Profile from '@/components/views/profile/Profile.vue'
import {User} from '@/store/profiles/types/User'

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
let vulpes: User

describe('Profile.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = new Router({
      mode: 'history',
      routes: [{
        path: '/',
        name: 'Home',
        component: Empty,
      }, {
        path: '/:username/',
        name: 'Profile',
        component: Empty,
        children: [
          {path: 'about', component: Empty, name: 'AboutUser'},
          {path: 'products', component: Empty, name: 'Products'},
          {path: 'characters', component: Empty, name: 'Characters'},
          {path: 'gallery', component: Empty, name: 'Gallery'},
          {path: 'favorite', component: Empty, name: 'Favorites'},
          {path: 'watchlists', component: Empty, name: 'Watchlists'},
        ],
      }, {
        path: '/login/',
        name: 'Login',
        component: Empty,
      },
      {
        path: '/:username/settings/',
        name: 'Settings',
        component: Empty,
      },
      {
        path: '/:username/messages/messageId/',
        name: 'Conversation',
        component: Empty,
      },
      ]})
    singleRegistry.reset()
    listRegistry.reset()
    formRegistry.reset()
    profileRegistry.reset()
    vuetifySetup()
    mockAxios.reset()
    vulpes = genUser()
    vulpes.username = 'Vulpes'
    vulpes.is_staff = false
    vulpes.is_superuser = false
    vulpes.id = 2
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Displays a Profile', async() => {
    setViewer(store, vulpes)
    const fox = genUser()
    fox.artist_mode = false
    router.push({name: 'Profile', params: {username: fox.username}})
    wrapper = mount(Profile, {
      localVue, store, router, propsData: {username: 'Fox'}, sync: false, attachToDocument: true}
    )
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/profiles/v1/account/Fox/', 'get'))
    mockAxios.mockResponse(rs(fox))
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/profiles/v1/account/Fox/artist-profile/', 'get', undefined, {
      params: {view: 'true'}, cancelToken: {},
    }))
    mockAxios.mockResponse(rs(genArtistProfile()))
    await flushPromises()
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe('AboutUser')
  })
  it('Displays a default route for an artist', async() => {
    setViewer(store, vulpes)
    const fox = genUser()
    fox.artist_mode = true
    router.push({name: 'Profile', params: {username: fox.username}})
    wrapper = mount(Profile, {
      localVue, store, router, propsData: {username: 'Fox'}, sync: false, attachToDocument: true}
    )
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/profiles/v1/account/Fox/', 'get'))
    mockAxios.mockResponse(rs(fox))
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/artist-profile/', 'get', undefined, {
        params: {view: 'true'}, cancelToken: {},
      })
    )
    mockAxios.mockResponse(rs(genArtistProfile()))
    await flushPromises()
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe('Products')
  })
  it('Sends a message', async() => {
    setViewer(store, vulpes)
    wrapper = mount(Profile, {
      localVue,
      store,
      router,
      propsData: {username: 'Fox'},
      sync: false,
      attachToDocument: true,
      stubs: ['ac-journals'],
    }
    )
    mockAxios.mockResponse(rs(genUser()))
    await wrapper.vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.message-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockAxios.post).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Vulpes/conversations/', 'post',
        {participants: [1]}, {})
    )
    mockAxios.mockResponse(rs(genConversation()))
    await flushPromises()
    await wrapper.vm.$nextTick()
  })
})
