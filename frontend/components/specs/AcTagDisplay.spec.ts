import {VueWrapper} from '@vue/test-utils'
import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers/index.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import AcTagDisplay from '@/components/AcTagDisplay.vue'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {searchSchema} from '@/lib/lib.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

let wrapper: VueWrapper<any>
let store: ArtStore
let form: FormController

const mockError = vi.spyOn(console, 'error')

describe('AcTagDisplay.vue', () => {
  beforeEach(() => {
    store = createStore()
    mockError.mockClear()
    form = mount(Empty, vueSetup({store})).vm.$getForm('search', searchSchema())
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
        mocks: {
          $route: {
            name: 'Profile',
            params: {username: 'Fox'},
            query: {editing: false},
          },
        },
        stubs: ['router-link'],
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
        mocks: {
          $route: {
            name: 'Profile',
            params: {username: 'Fox'},
            query: {editing: false},
          },
        },
        stubs: ['router-link'],
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
        mocks: {
          $route: {
            name: 'Profile',
            params: {
              username: 'Fox',
              scope: 'Submissions',
            },
            query: {editing: false},
          },
        },
        stubs: ['router-link'],
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
    wrapper = mount(AcTagDisplay, {
      ...vueSetup({
        store,
        mocks: {
          $route: {
            name: 'Profile',
            params: {username: 'Vulpes'},
            query: {editing: false},
          },
        },
        stubs: ['router-link'],
      }),
      props: {
        patcher: single.patchers.tags,
        username: 'Vulpes',
        scope: 'Submissions',
        editable: false,
      },
    })
    const vm = wrapper.vm as any
    expect(vm.controls).toBe(true)
  })
  test('Edits the search query', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    submission.tags = ['fox', 'sexy', 'fluffy', 'herm']
    const single = mount(Empty, vueSetup({store})).vm.$getSingle('submission', {endpoint: '/'})
    single.setX(submission)
    const push = vi.fn()
    wrapper = mount(AcTagDisplay, {
      ...vueSetup({
        store,
        mocks: {
          $route: {
            name: 'Profile',
            params: {username: 'Fox'},
            query: {editing: false},
          },
          $router: {push},
        },
        stubs: ['router-link'],
      }),
      props: {
        patcher: single.patchers.tags,
        username: 'Fox',
        scope: 'Submissions',
      },
    })
    await wrapper.find('.tag-search-link').trigger('click')
    await wrapper.vm.$nextTick()
    expect(form.fields.q.value).toEqual('fox')
    expect(push).toHaveBeenCalledWith({
      name: 'SearchSubmissions',
      query: {q: 'fox'},
    })
  })
})
