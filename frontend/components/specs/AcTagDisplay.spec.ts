import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {singleRegistry} from '@/store/singles/registry'
import {profileRegistry} from '@/store/profiles/registry'
import {setViewer, vueSetup, vuetifySetup} from '@/specs/helpers'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ArtStore, createStore} from '@/store'
import AcTagDisplay from '@/components/AcTagDisplay.vue'
import {genUser} from '@/specs/helpers/fixtures'
import {searchSchema} from '@/lib'
import {formRegistry} from '@/store/forms/registry'
import {FormController} from '@/store/forms/form-controller'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let form: FormController

const mockError = jest.spyOn(console, 'error')

describe('AcTagDisplay.vue', () => {
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    singleRegistry.reset()
    profileRegistry.reset()
    formRegistry.reset()
    mockError.mockClear()
    form = mount(Empty, {localVue, store}).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Loads and displays tags', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    submission.tags = ['fox', 'sexy', 'fluffy', 'herm']
    const single = mount(Empty, {localVue, store}).vm.$getSingle('submission', {endpoint: '/'})
    single.setX(submission)
    wrapper = mount(AcTagDisplay, {
      localVue,
      store,
      propsData: {patcher: single.patchers.tags, username: 'Fox', scope: 'Submissions'},
      mocks: {$route: {name: 'Profile', params: {username: 'Fox'}, query: {editing: false}}},
      stubs: ['router-link'],
      sync: false,
      attachToDocument: false,
    })
  })
  it('Exposes an editing interface', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    submission.tags = ['fox', 'sexy', 'fluffy', 'herm']
    const single = mount(Empty, {localVue, store}).vm.$getSingle('submission', {endpoint: '/'})
    single.setX(submission)
    wrapper = mount(AcTagDisplay, {
      localVue,
      store,
      propsData: {patcher: single.patchers.tags, username: 'Fox', scope: 'Submissions'},
      mocks: {$route: {name: 'Profile', params: {username: 'Fox'}, query: {editing: false}}},
      stubs: ['router-link'],
      sync: false,
      attachToDocument: false,
    })
    const vm = wrapper.vm as any
    expect(vm.toggle).toBe(false)
    expect(vm.editing).toBe(false)
    wrapper.find('.edit-button').trigger('click')
    await vm.$nextTick()
    expect(vm.toggle).toBe(true)
    expect(vm.editing).toBe(true)
  })
  it('Expands to show all tags', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    submission.tags = ['fox', 'sexy', 'fluffy', 'herm', 'dude', 'wat', 'stuff', 'things', 'fuck', 'paws', 'maws']
    const single = mount(Empty, {localVue, store}).vm.$getSingle('submission', {endpoint: '/'})
    single.setX(submission)
    wrapper = mount(AcTagDisplay, {
      localVue,
      store,
      propsData: {patcher: single.patchers.tags, username: 'Fox', scope: 'Submissions'},
      mocks: {$route: {name: 'Profile', params: {username: 'Fox', scope: 'Submissions'}, query: {editing: false}}},
      stubs: ['router-link'],
      sync: false,
      attachToDocument: false,
    })
    const vm = wrapper.vm as any
    expect(vm.toggle).toBe(false)
    expect(vm.editing).toBe(false)
    wrapper.find('.show-more-tags').trigger('click')
    await vm.$nextTick()
    expect(vm.toggle).toBe(true)
    expect(vm.editing).toBe(false)
  })
  it('Always allows staff to edit', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    submission.tags = ['fox', 'sexy', 'fluffy', 'herm', 'dude', 'wat']
    const empty = mount(Empty, {localVue, store})
    const single = empty.vm.$getSingle('submission', {endpoint: '/'})
    const otherUser = empty.vm.$getProfile('Vulpes', {})
    const vulpes = genUser()
    vulpes.username = 'Vulpes'
    otherUser.user.setX(vulpes)
    single.setX(submission)
    wrapper = mount(AcTagDisplay, {
      localVue,
      store,
      propsData: {
        patcher: single.patchers.tags, username: 'Vulpes', scope: 'Submissions', editable: false,
      },
      mocks: {$route: {name: 'Profile', params: {username: 'Vulpes'}, query: {editing: false}}},
      stubs: ['router-link'],
      sync: false,
      attachToDocument: false,
    })
    const vm = wrapper.vm as any
    expect(vm.controls).toBe(true)
  })
  it('Edits the search query', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    submission.tags = ['fox', 'sexy', 'fluffy', 'herm']
    const single = mount(Empty, {localVue, store}).vm.$getSingle('submission', {endpoint: '/'})
    single.setX(submission)
    const push = jest.fn()
    wrapper = mount(AcTagDisplay, {
      localVue,
      store,
      propsData: {patcher: single.patchers.tags, username: 'Fox', scope: 'Submissions'},
      mocks: {$route: {name: 'Profile', params: {username: 'Fox'}, query: {editing: false}}, $router: {push}},
      stubs: ['router-link'],
      sync: false,
      attachToDocument: false,
    })
    wrapper.find('.tag-search-link').trigger('click')
    await wrapper.vm.$nextTick()
    expect(form.fields.q.value).toEqual('fox')
    expect(push).toHaveBeenCalledWith({name: 'SearchSubmissions', query: {q: 'fox'}})
  })
})
