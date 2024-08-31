import {createRouter, createWebHistory, Router} from 'vue-router'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import WatchList from '@/components/views/profile/WatchList.vue'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

describe('WatchList.vue', () => {
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
        name: 'Dummy',
        path: '/dummy',
        component: Empty,
        props: true,
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts and loads a watchlist', async() => {
    setViewer({ store, user: genUser() })
    // Need a route for the paginator to check page numbers on. Can be any.
    await router.push({name: 'Dummy'})
    wrapper = mount(WatchList, {
      ...vueSetup({
        store,
router,
      }),
      props: {
        username: 'Fox',
        nameSpace: 'watching',
        endpoint: '/test/',
      },
    })
    const vm = wrapper.vm as any
    vm.watch.setList([genUser()])
    vm.watch.fetching = false
    vm.watch.ready = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.ac-avatar').exists()).toBe(true)
  })
})
