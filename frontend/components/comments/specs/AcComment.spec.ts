import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {
  cleanUp,
  confirmAction, createVuetify,
  flushPromises,
  mount,
  rq,
  rs,
  vueSetup,
  VuetifyWrapped, waitFor, waitForSelector,
} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {commentSet} from './fixtures.ts'
import AcComment from '@/components/comments/AcComment.vue'
import {Router, createRouter, createWebHistory} from 'vue-router'
import mockAxios from '@/__mocks__/axios.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import {setViewer} from '@/lib/lib.ts'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

const WrappedAcComment = VuetifyWrapped(AcComment)

describe('AcComment.vue', () => {
  beforeEach(() => {
    vi.useFakeTimers()
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
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Handles a comment', async() => {
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[0],
        username: commentList.list[0].x.user.username,
      },
    })
    expect(wrapper.find('.alternate').exists()).toBe(false)
    expect(wrapper.find('.subcomments').exists()).toBe(false)
  })
  test('Handles a nullified comment', async() => {
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[0],
        username: '',
      },
    })
    commentList.list[0].markDeleted()
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.alternate').exists()).toBe(false)
    expect(wrapper.find('.subcomments').exists()).toBe(false)
  })
  test('Handles a comment with children', async() => {
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[1],
        username: commentList.list[1].x.user.username,
      },
    })
    await waitForSelector(wrapper, '.subcomments')
  })
  test('Scrolls to the comment if it is to be highlighted', async() => {
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    await router.replace({
      name: 'Home',
      query: {commentId: '17'},
    })
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[0],
        username: commentList.list[0].x.user.username,
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$refs.vm.scrolled).toBe(true)
  })
  test('Sets an alternate coloration', async() => {
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[1],
        username: commentList.list[1].x.user.username,
        alternate: true,
      },
    })
    expect(wrapper.find('.alternate').exists()).toBe(true)
  })
  test('Allows for a reply', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[0],
        username: commentList.list[0].x.user.username,
        nesting: true,
      },
    })
    const replyButton = wrapper.find('.reply-button')
    expect(replyButton.exists()).toBe(true)
    await replyButton.trigger('click')
    await waitForSelector(wrapper, '.new-comment textarea')
    await wrapper.find('.new-comment textarea').setValue('Response comment!')
    await wrapper.find('.new-comment .cancel-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.new-comment textarea').exists()).toBe(false)
  })
  test('Allows for a reply by another user', async() => {
    const user = genUser()
    user.id = 234
    user.username = 'Vulpes'
    user.is_staff = false
    user.is_superuser = false
    setViewer(store, user)
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    const comments = {...commentSet, ...{results: [commentSet.results[0]]}}
    commentList.response = {...comments}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[0],
        username: 'Fox',
        nesting: true,
      },
    })
    const replyButton = await wrapper.find('.reply-button')
    expect(replyButton.exists()).toBe(true)
    await replyButton.trigger('click')
    await wrapper.vm.$nextTick()
    await waitForSelector(wrapper, '.new-comment textarea')
    await wrapper.find('.new-comment textarea').setValue('Response comment!')
    await wrapper.find('.new-comment .cancel-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.new-comment textarea').exists()).toBe(false)
  })
  test('Does not allow for a reply when nesting is disabled', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[0],
        username: commentList.list[0].x.user.username,
        nesting: false,
      },
    })
    expect(wrapper.find('.reply-button').exists()).toBe(false)
  })
  test('Edits a comment', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[0],
        username: commentList.list[0].x.user.username,
        nesting: false,
      },
    })
    await wrapper.find('.more-button').trigger('click')
    await wrapper.vm.$nextTick()
    await wrapper.find('.edit-button').trigger('click')
    await wrapper.vm.$nextTick()
    await waitForSelector(wrapper, 'textarea')
    await wrapper.find('textarea').setValue('Edited message')
    await wrapper.vm.$nextTick()
    await wrapper.find('.save-button').trigger('click')
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/comments/17/', 'patch', {text: 'Edited message'}, {signal: expect.any(Object)}),
    )
    mockAxios.mockResponse(rs({
      id: 17,
      text: 'Edited message',
      created_on: '2019-06-26T05:38:35.922476-05:00',
      edited_on: '2019-06-26T05:38:35.922499-05:00',
      user: {
        id: 3,
        username: 'Fox',
        avatar_url: 'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
        stars: '4.25',
        is_staff: true,
        is_superuser: true,
        guest: false,
        artist_mode: null,
      },
      comments: [],
      comment_count: 0,
      edited: true,
      deleted: false,
      subscribed: true,
      system: false,
    }))
  })
  test('Deletes a comment', async() => {
    setViewer(store, genUser({is_staff: true}))
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[2],
        username: null,
        nesting: false,
      },
    })
    expect((wrapper.vm as any).$refs.vm.comment.x).toBeTruthy()
    await wrapper.vm.$nextTick()
    mockAxios.reset()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    await wrapper.vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/comments/13/', 'delete'),
    )
    mockAxios.mockResponse(rs(null))
    await flushPromises()
    expect((wrapper.vm as any).$refs.vm.comment.x).toBe(null)
    expect((wrapper.vm as any).$refs.vm.comment.deleted).toBe(true)
    expect((wrapper.vm as any).$refs.vm.comment.ready).toBe(false)
  })
  test('Deletes a thread', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[2],
        username: null,
        nesting: false,
      },
    })
    const vm = wrapper.vm.$refs.vm as any
    expect(vm.comment.x).toBeTruthy()
    vm.comment.updateX({deleted: true})
    await vm.$nextTick()
    expect(vm.comment.x).toBeTruthy()
    for (const comment of vm.subCommentList.list) {
      comment.setX(null)
    }
    await vm.$nextTick()
    expect(vm.comment.x).toBe(null)
  })
  test('Does not delete a thread in history mode', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[2],
        username: null,
        nesting: false,
        showHistory: true,
      },
    })
    const vm = wrapper.vm.$refs.vm as any
    expect(vm.comment.x).toBeTruthy()
    vm.comment.updateX({deleted: true})
    await vm.$nextTick()
    expect(vm.comment.x).toBeTruthy()
    for (const comment of vm.subCommentList.list) {
      comment.setX(false)
    }
    await vm.$nextTick()
    expect(vm.comment.x).toBeTruthy()
  })
  test('Does not delete a thread when displaying actual history', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[2],
        username: null,
        nesting: false,
        inHistory: true,
      },
    })
    const vm = wrapper.vm.$refs.vm as any
    expect(vm.comment.x).toBeTruthy()
    vm.comment.updateX({deleted: true})
    await vm.$nextTick()
    expect(vm.comment.x).toBeTruthy()
    for (const comment of vm.subCommentList.list) {
      comment.setX(false)
    }
    await vm.$nextTick()
    expect(vm.comment.x).toBeTruthy()
  })
  test('Renders historical comments', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, vueSetup({store}))
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList([...commentSet.results])
    wrapper = mount(WrappedAcComment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        commentList,
        comment: commentList.list[2],
        username: null,
        nesting: false,
        showHistory: true,
      },
    })
    mockAxios.reset()
    const vm = wrapper.vm.$refs.vm as any
    await wrapper.find('.more-button').trigger('click')
    await vm.$nextTick()
    await wrapper.find('.history-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockAxios.lastReqGet().url).toBe('/api/lib/comments/lib.Comment/13/history/')
    vm.historyList.response = {...commentSet}
    vm.historyList.setList([...commentSet.results])
    vm.historyList.fetching = false
    vm.historyList.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.v-dialog .comment').exists()).toBe(true)
  })
})
