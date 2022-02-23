import Vue from 'vue'
import Router from 'vue-router'
import {cleanUp, createVuetify, rq, setViewer, vueSetup, mount} from '@/specs/helpers'
import {Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import mockAxios from '@/__mocks__/axios'
import {commentSet} from '@/components/comments/specs/fixtures'
import {genUser} from '@/specs/helpers/fixtures'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify
const mockError = jest.spyOn(console, 'error')

describe('AcCommentSection', () => {
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
          {path: 'about', name: 'AboutUser', component: Empty},
        ],
      }, {
        path: '/login/:tabName/',
        name: 'Login',
        component: Empty,
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
    mockError.mockReset()
  })
  it('Fetches and renders a comment list', async() => {
    setViewer(store, genUser())
    const commentList = mount(Empty, {localVue, store}).vm.$getList('commentList', {
      endpoint: '/api/comments/',
      reverse: true,
    })
    wrapper = mount(AcCommentSection, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        showHistory: false,
        commentList,
      },
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/comments/', 'get', undefined, {
      params: {page: 1, size: 24}, cancelToken: expect.any(Object),
    }))
    commentList.response = commentSet
    commentList.setList(commentSet.results)
    commentList.fetching = false
    commentList.ready = true
    await vm.$nextTick()
    expect(wrapper.findAll('.comment').length).toBe(7)
  })
  it('Throws an error if you try to load an unreversedlist', async() => {
    mockError.mockImplementationOnce(() => {})
    const commentList = mount(Empty, {localVue, store}).vm.$getList('commentList', {
      endpoint: '/api/comments/',
    })
    expect(() => {
      wrapper = mount(AcCommentSection, {
        localVue,
        store,
        router,
        vuetify,

        propsData: {
          showHistory: true,
          commentList,
        },
      })
    }).toThrow('Comment lists should always be reversed!')
  })
  it('Toggle history mode', async() => {
    setViewer(store, genUser())
    const commentList = mount(Empty, {localVue, store}).vm.$getList('commentList', {
      endpoint: '/api/comments/',
      reverse: true,
    })
    wrapper = mount(AcCommentSection, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        showHistory: true,
        commentList,
      },
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/comments/', 'get', undefined, {
      cancelToken: expect.any(Object), params: {page: 1, size: 24},
    }))
    mockAxios.reset()
    wrapper.find('.comment-history-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/comments/', 'get', undefined, {
      params: {history: '1', page: 1, size: 24}, cancelToken: expect.any(Object),
    }))
    mockAxios.reset()
    wrapper.find('.comment-history-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/comments/', 'get', undefined, {
      cancelToken: expect.any(Object), params: {page: 1, size: 24},
    }))
  })
})
