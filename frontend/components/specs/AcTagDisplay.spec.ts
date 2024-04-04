import {VueWrapper} from '@vue/test-utils'
import {cleanUp, mount, vueSetup, createTestRouter, VuetifyWrapped, waitFor} from '@/specs/helpers/index.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import AcTagDisplay from '@/components/AcTagDisplay.vue'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {searchSchema, setViewer} from '@/lib/lib.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {Router} from 'vue-router'
import {nextTick} from 'vue'

let wrapper: VueWrapper<any>
let store: ArtStore
let form: FormController
let router: Router

const mockError = vi.spyOn(console, 'error')
const WrappedTagDisplay = VuetifyWrapped(AcTagDisplay)

describe('AcTagDisplay.vue', () => {
  beforeEach(() => {
    store = createStore()
    mockError.mockClear()
    form = mount(Empty, vueSetup({store})).vm.$getForm('search', searchSchema())
    router = createTestRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Loads and displays tags', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    submission.tags = ['fox', 'sexy', 'fluffy', 'herm']
    const single = mount(Empty, vueSetup({store})).vm.$getSingle('submission', {endpoint: '/'})
    single.setX(submission)
    wrapper = mount(AcTagDisplay, {
      ...vueSetup({
        store,
router,
      }),
      props: {
        patcher: single.patchers.tags,
        username: 'Fox',
        scope: 'Submissions',
      },
    })
  })
  test('Exposes an editing interface', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    submission.tags = ['fox', 'sexy', 'fluffy', 'herm']
    const single = mount(Empty, vueSetup({store})).vm.$getSingle('submission', {endpoint: '/'})
    single.setX(submission)
    wrapper = mount(AcTagDisplay, {
      ...vueSetup({
        store,
router,
      }),
      props: {
        patcher: single.patchers.tags,
        username: 'Fox',
        scope: 'Submissions',
      },
    })
    const vm = wrapper.vm as any
    expect(vm.toggle).toBe(false)
    expect(vm.editing).toBe(false)
    await wrapper.find('.edit-button').trigger('click')
    await vm.$nextTick()
    expect(vm.toggle).toBe(true)
    expect(vm.editing).toBe(true)
  })
  test('Expands to show all tags', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    submission.tags = ['fox', 'sexy', 'fluffy', 'herm', 'dude', 'wat', 'stuff', 'things', 'fuck', 'paws', 'maws']
    const single = mount(Empty, vueSetup({store})).vm.$getSingle('submission', {endpoint: '/'})
    single.setX(submission)
    wrapper = mount(AcTagDisplay, {
      ...vueSetup({
        store,
router,
      }),
      props: {
        patcher: single.patchers.tags,
        username: 'Fox',
        scope: 'Submissions',
      },
    })
    const vm = wrapper.vm as any
    expect(vm.toggle).toBe(false)
    expect(vm.editing).toBe(false)
    await wrapper.find('.show-more-tags').trigger('click')
    await vm.$nextTick()
    expect(vm.toggle).toBe(true)
    expect(vm.editing).toBe(false)
  })
  test('Always allows staff to edit', async() => {
    setViewer(store, genUser({is_staff: true}))
    const submission = genSubmission()
    submission.tags = ['fox', 'sexy', 'fluffy', 'herm', 'dude', 'wat']
    const empty = mount(Empty, vueSetup({store}))
    const single = empty.vm.$getSingle('submission', {endpoint: '/'})
    const otherUser = empty.vm.$getProfile('Vulpes', {})
    const vulpes = genUser()
    vulpes.username = 'Vulpes'
    otherUser.user.setX(vulpes)
    single.setX(submission)
    wrapper = mount(WrappedTagDisplay, {
      ...vueSetup({
        store,
router,
      }),
      props: {
        patcher: single.patchers.tags,
        username: 'Vulpes',
        scope: 'Submissions',
        editable: false,
      },
    })
    await nextTick()
    // Why is this torture necessary?
    const vm = (wrapper.findComponent(AcTagDisplay) as unknown as VueWrapper<typeof AcTagDisplay>).vm
    expect(vm.controls).toBe(true)
  })
  test('Edits the search query', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    submission.tags = ['fox', 'sexy', 'fluffy', 'herm']
    const single = mount(Empty, vueSetup({store})).vm.$getSingle('submission', {endpoint: '/'})
    single.setX(submission)
    await router.push('/')
    wrapper = mount(AcTagDisplay, {
      ...vueSetup({
        store,
router,
      }),
      props: {
        patcher: single.patchers.tags,
        username: 'Fox',
        scope: 'Submissions',
      },
    })
    await wrapper.find('.tag-search-link').trigger('click')
    await nextTick()
    expect(form.fields.q.value).toEqual('fox')
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('SearchSubmissions'))
    expect(router.currentRoute.value.query.q).toEqual('fox')
  })
})
