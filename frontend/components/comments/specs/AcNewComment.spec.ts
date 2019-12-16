import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, flushPromises, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {commentSet} from './fixtures'
import Router from 'vue-router'
import mockAxios from '@/__mocks__/axios'
import AcNewComment from '@/components/comments/AcNewComment.vue'
import {Vuetify} from 'vuetify/types'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('AcNewComment.vue', () => {
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
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Posts a new comment', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    expect(commentList.list.length).toEqual(3)
    wrapper = mount(AcNewComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[0],
        username: commentList.list[0].x.user.username,
      },
      sync: false,
      attachToDocument: true,
    })
    wrapper.find('textarea').setValue('New comment!')
    await wrapper.vm.$nextTick()
    wrapper.find('.submit-button').trigger('click')
    expect(mockAxios.post).toHaveBeenCalledWith(
      ...rq('/api/comments/', 'post', {text: 'New comment!'}, {})
    )
    mockAxios.mockResponse(rs({
      id: 17,
      text: 'New comment!',
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
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(commentList.list.length).toEqual(4)
  })
})
