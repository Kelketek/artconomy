import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {
  cleanUp,
  confirmAction, createTestRouter,
  flushPromises,
  mount,
  rq,
  rs,
  vueSetup,
  VuetifyWrapped, waitFor,
} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {createRouter, createWebHistory, Router} from 'vue-router'
import mockAxios from '@/__mocks__/axios.ts'
import Journal from '@/components/views/JournalDetail.vue'
import {genJournal} from '@/components/views/specs/fixtures.ts'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'
import {setViewer} from '@/lib/lib.ts'
import {VMenu} from 'vuetify/components'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router


describe('Journal.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = createTestRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts a journal', async() => {
    wrapper = mount(Journal, {
        ...vueSetup({
          store,
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
    wrapper = mount(Journal, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-comment-section'],
      }),
      props: {
        journalId: 1,
        username: 'Fox',
      },
    })
    const vm = wrapper.vm
    vm.journal.makeReady(genJournal())
    mockAxios.reset()
    await wrapper.vm.$nextTick()
    await wrapper.find('.more-button').trigger('click')
    const toggle = await waitFor(() => wrapper.findComponent('.edit-toggle'))
    expect(toggle.exists()).toBe(true)
    await toggle.trigger('click')
    await wrapper.vm.$nextTick()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    const mockDelete = mockAxios.getReqByUrl('/api/profiles/account/Fox/journals/1/')
    expect(mockDelete.method).toBe('delete')
    mockAxios.mockResponse(rs(null), mockDelete)
    await waitFor(() => expect(router.currentRoute.value.path).toBe('/profile/Fox/'))
  })
})
