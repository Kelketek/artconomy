import {Router, createRouter, createWebHistory} from 'vue-router'
import {cleanUp, mount, rq, setViewer, vueSetup, VuetifyWrapped} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {commentSet} from '@/components/comments/specs/fixtures.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import AcComment from '@/components/comments/AcComment.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router
const mockError = vi.spyOn(console, 'error')

const WrappedCommentSection = VuetifyWrapped(AcCommentSection)

describe('AcCommentSection', () => {
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: [{
        path: '/',
        name: 'Home',
        component: Empty,
      }, {
        path: '/:username/',
        name: 'Profile',
        component: Empty,
        children: [
          {
            path: 'about',
            name: 'AboutUser',
            component: Empty,
          },
        ],
      }, {
        path: '/login/',
        name: 'Login',
        component: Empty,
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
    mockError.mockReset()
  })
  test('Fetches and renders a comment list', async() => {
    setViewer(store, genUser())
    const commentList = mount(Empty, vueSetup({store})).vm.$getList('commentList', {
      endpoint: '/api/comments/',
      reverse: true,
    })
    wrapper = mount(WrappedCommentSection, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        showHistory: false,
        commentList,
      },
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/comments/', 'get', undefined, {
      params: {
        page: 1,
        size: 24,
      },
      signal: expect.any(Object),
    }))
    commentList.response = commentSet
    commentList.setList(commentSet.results)
    commentList.fetching = false
    commentList.ready = true
    await vm.$nextTick()
    expect(wrapper.findAll('.comment').length).toBe(7)
  })
  test('Throws an error if you try to load an unreversedlist', async() => {
    mockError.mockImplementationOnce(() => {
    })
    const commentList = mount(Empty, vueSetup({store})).vm.$getList('commentList', {
      endpoint: '/api/comments/',
    })
    expect(() => {
      wrapper = mount(WrappedCommentSection, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          components: {
            AcComment,
            AcCommentSection,
          },
        }),
        props: {
          showHistory: true,
          commentList,
        },
      })
    }).toThrow('Comment lists should always be reversed!')
  })
  test('Toggle history mode', async() => {
    setViewer(store, genUser())
    const commentList = mount(Empty, vueSetup({store})).vm.$getList('commentList', {
      endpoint: '/api/comments/',
      reverse: true,
    })
    wrapper = mount(WrappedCommentSection, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        showHistory: true,
        commentList,
      },
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/comments/', 'get', undefined, {
      signal: expect.any(Object),
      params: {
        page: 1,
        size: 24,
      },
    }))
    mockAxios.reset()
    await wrapper.find('.comment-history-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/comments/', 'get', undefined, {
      params: {
        history: '1',
        page: 1,
        size: 24,
      },
      signal: expect.any(Object),
    }))
    mockAxios.reset()
    await wrapper.find('.comment-history-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/comments/', 'get', undefined, {
      signal: expect.any(Object),
      params: {
        page: 1,
        size: 24,
      },
    }))
  })
})
