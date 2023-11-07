import {createRouter, createWebHistory, Router} from 'vue-router'
import {cleanUp, confirmAction, flushPromises, mount, rs, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {VueWrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty'
import {genUser} from '@/specs/helpers/fixtures'
import ConversationDetail from '@/components/views/ConversationDetail.vue'
import {genConversation} from '@/components/views/specs/fixtures'
import mockAxios from '@/__mocks__/axios'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

describe('ConversationDetail.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: [{
        name: 'Profile',
        path: '/profiles/:username/',
        component: Empty,
        props: true,
      }, {
        name: 'AboutUser',
        path: '/profiles/:username/products/',
        component: Empty,
        props: true,
      }, {
        name: 'BuyAndSell',
        path: '/faq/buy-and-sell',
        component: Empty,
        props: true,
      }, {
        name: 'Conversations',
        path: '/messages/:username/',
        component: Empty,
        props: true,
      }, {
        name: 'Home',
        path: '/',
        component: Empty,
        props: true,
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Loads a lock toggle for an outside user', async() => {
    const user = genUser()
    user.username = 'Dude'
    setViewer(store, user)
    const wrapper = mount(ConversationDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Fox',
        conversationId: 23,
      },
    })
    const vm = wrapper.vm as any
    vm.conversation.setX(genConversation())
    vm.conversation.fetching = false
    vm.conversation.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.lock-toggle').exists()).toBe(true)
  })
  test('Does not load a lock toggle for an inside user', async() => {
    const user = genUser()
    setViewer(store, user)
    const wrapper = mount(ConversationDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Fox',
        conversationId: 23,
      },
    })
    const vm = wrapper.vm as any
    vm.conversation.setX(genConversation())
    vm.conversation.fetching = false
    vm.conversation.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.lock-toggle').exists()).toBe(false)
  })
  test('Leaves a conversation', async() => {
    const user = genUser()
    setViewer(store, user)
    const wrapper = mount(ConversationDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Fox',
        conversationId: 23,
      },
    })
    const vm = wrapper.vm as any
    await router.isReady()
    vm.conversation.setX(genConversation())
    vm.conversation.fetching = false
    vm.conversation.ready = true
    await vm.$nextTick()
    mockAxios.reset()
    await confirmAction(wrapper, ['.delete-button'])
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    await vm.$nextTick()
    expect(router.currentRoute.value.name).toBe('Conversations')
  })
})
