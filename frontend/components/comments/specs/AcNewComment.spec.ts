import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {ArtStore, createStore} from '@/store'
import {flushPromises, rq, rs, setViewer, vuetifySetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {commentSet} from './fixtures'
import {listRegistry, Lists} from '@/store/lists/registry'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import Router from 'vue-router'
import mockAxios from '@/__mocks__/axios'
import AcNewComment from '@/components/comments/AcNewComment.vue'

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

describe('AcNewComment.vue', () => {
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
