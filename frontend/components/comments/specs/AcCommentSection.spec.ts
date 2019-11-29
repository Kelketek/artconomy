import Vue from 'vue'
import Router from 'vue-router'
import {cleanUp, rq, setViewer, vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import mockAxios from '@/__mocks__/axios';
import {commentSet} from '@/components/comments/specs/fixtures'
import {genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router

describe('AcCommentSection', () => {
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
        path: '/login/:tabName/',
        name: 'Login',
        component: Empty,
      }]})
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Fetches and renders a comment list', async() => {
    setViewer(store, genUser())
    const commentList = mount(Empty, {localVue, store}).vm.$getList('commentList', {endpoint: '/api/comments/'})
    wrapper = mount(AcCommentSection, {
      localVue,
      store,
      router,
      attachToDocument: false,
      sync: false,
      propsData: {
        showHistory: false,
        commentList,
      }})
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/comments/', 'get', undefined, {
      params: {page: 1, size: 24}, cancelToken: {},
    }))
    commentList.response = commentSet
    commentList.setList(commentSet.results)
    commentList.fetching = false
    commentList.ready = true
    await vm.$nextTick()
    expect(wrapper.findAll('.comment').length).toBe(7)
  })
  it('Toggle history mode', async() => {
    setViewer(store, genUser())
    const commentList = mount(Empty, {localVue, store}).vm.$getList('commentList', {endpoint: '/api/comments/'})
    wrapper = mount(AcCommentSection, {
      localVue,
      store,
      router,
      attachToDocument: false,
      sync: false,
      propsData: {
        showHistory: true,
        commentList,
      }})
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/comments/', 'get', undefined, {
      cancelToken: {}, params: {page: 1, size: 24},
    }))
    mockAxios.reset()
    wrapper.find('.comment-history-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/comments/', 'get', undefined, {
      params: {history: '1', page: 1, size: 24}, cancelToken: {},
    }))
    mockAxios.reset()
    wrapper.find('.comment-history-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/api/comments/', 'get', undefined, {
      cancelToken: {}, params: {page: 1, size: 24},
    }))
  })
})
