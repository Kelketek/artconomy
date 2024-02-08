import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {
  cleanUp,
  confirmAction,
  flushPromises,
  mount,
  rq,
  rs,
  setViewer,
  vueSetup,
  VuetifyWrapped,
} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {createRouter, createWebHistory, Router} from 'vue-router'
import mockAxios from '@/__mocks__/axios.ts'
import Journal from '@/components/views/JournalDetail.vue'
import {genJournal} from '@/components/views/specs/fixtures.ts'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

const WrappedJournal = VuetifyWrapped(Journal)

describe('Journal.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: [{
        path: '/',
        name: 'Home',
        component: Empty,
      }, {
        path: '/:username',
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
      },
      ],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts a journal', async() => {
    wrapper = mount(Journal, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-comment-section'],
        }),
        props: {
          journalId: 1,
          username: 'Fox',
        },
      },
    )
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/account/Fox/journals/1/', 'get'))
    expect(wrapper.find('.edit-toggle').exists()).toBe(false)
    expect(wrapper.find('.delete-button').exists()).toBe(false)
  })
  test('Deletes a journal', async() => {
    await router.push('/')
    setViewer(store, genUser({is_staff: true}))
    wrapper = mount(WrappedJournal, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        stubs: ['ac-comment-section'],
      }),
      props: {
        journalId: 1,
        username: 'Fox',
      },
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.journal.makeReady(genJournal())
    mockAxios.reset()
    await wrapper.vm.$nextTick()
    await wrapper.find('.more-button').trigger('click')
    const toggle = wrapper.find('.edit-toggle')
    expect(toggle.exists()).toBe(true)
    await toggle.trigger('click')
    await wrapper.vm.$nextTick()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    const mockDelete = mockAxios.getReqByUrl('/api/profiles/account/Fox/journals/1/')
    expect(mockDelete.method).toBe('delete')
    mockAxios.mockResponse(rs(null), mockDelete)
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.value.path).toBe('/Fox')
  })
})
