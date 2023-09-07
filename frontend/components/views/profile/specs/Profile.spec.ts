import Vue from 'vue'
import {Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, docTarget, flushPromises, rq, rs, setViewer, vueSetup, mount} from '@/specs/helpers'
import {genArtistProfile, genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import Router from 'vue-router'
import mockAxios from '@/__mocks__/axios'
import Profile from '@/components/views/profile/Profile.vue'
import {User} from '@/store/profiles/types/User'
import {genConversation} from '@/components/views/specs/fixtures'
import {genPricing} from '@/lib/specs/helpers'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vulpes: User
let vuetify: Vuetify

describe('Profile.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
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
      ],
    })
    vulpes = genUser()
    vulpes.username = 'Vulpes'
    vulpes.is_staff = false
    vulpes.is_superuser = false
    vulpes.id = 2
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Displays a Profile', async() => {
    setViewer(store, vulpes)
    const fox = genUser()
    fox.artist_mode = false
    router.push({name: 'Profile', params: {username: fox.username}})
    wrapper = mount(Profile, {localVue, store, router, vuetify, propsData: {username: 'Fox'}, attachTo: docTarget()},
    )
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/account/Fox/', 'get'))
    mockAxios.mockResponse(rs(genPricing()))
    mockAxios.mockResponse(rs(fox))
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/account/Fox/artist-profile/', 'get', undefined, {
      params: {view: 'true'}, cancelToken: expect.any(Object),
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
    wrapper = mount(Profile, {localVue, store, router, vuetify, propsData: {username: 'Fox'}, attachTo: docTarget()})
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/account/Fox/', 'get'))
    mockAxios.mockResponse(rs(genPricing()))
    mockAxios.mockResponse(rs(fox))
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Fox/artist-profile/', 'get', undefined, {
        params: {view: 'true'}, cancelToken: expect.any(Object),
      }),
    )
    mockAxios.mockResponse(rs(genArtistProfile()))
    await flushPromises()
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe('AboutUser')
  })
  it('Starts a conversation', async() => {
    setViewer(store, vulpes)
    const fox = genUser()
    fox.artist_mode = false
    router.push({name: 'Profile', params: {username: fox.username}})
    wrapper = mount(Profile, {localVue, store, router, vuetify, propsData: {username: 'Fox'}, attachTo: docTarget()})
    mockAxios.mockResponse(rs(genPricing()))
    mockAxios.mockResponse(rs(fox))
    mockAxios.reset()
    await wrapper.vm.$nextTick()
    wrapper.find('.message-button').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('.dialog-submit').trigger('click')
    const response = genConversation()
    mockAxios.mockResponse(rs(response))
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.name).toBe('Conversation')
  })
})
