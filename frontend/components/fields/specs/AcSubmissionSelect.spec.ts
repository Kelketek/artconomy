import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {cleanUp, genAnon, setViewer, vueSetup} from '@/specs/helpers'
import AcSubmissionSelect from '@/components/fields/AcSubmissionSelect.vue'
import {ArtStore, createStore} from '@/store'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const localVue = vueSetup()
let store: ArtStore
jest.useFakeTimers()
let wrapper: Wrapper<Vue>

describe('AcSubmissionSelect.vue', () => {
  beforeEach(() => {
    store = createStore()
    setViewer(store, genAnon())
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
    cleanUp()
  })
  it('Gets the right comparison ID when comparison is specified', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        localVue,
        store,
        propsData: {
          value: 2, queryEndpoint: '/stuff/', saveComparison: currentSubmission,
        },
        sync: false,
        attachToDocument: true,
        stubs: ['router-link'],
      }
    )
    const vm = wrapper.vm as any
    const submissions = [currentSubmission, genSubmission(), genSubmission()]
    submissions[1].id = 2
    submissions[2].id = 3
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {count: 3, size: 10}
    await wrapper.vm.$nextTick()
    expect(vm.compare).toBe(1)
  })
  it('Gets the right comparison ID when comparison is specified and the related switch is enabled', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        localVue,
        store,
        propsData: {
          value: 2,
          queryEndpoint: '/stuff/',
          saveComparison: currentSubmission,
          related: true,
        },
        sync: false,
        attachToDocument: true,
        stubs: ['router-link'],
      }
    )
    const vm = wrapper.vm as any
    const submissions = [
      {id: 4, submission: currentSubmission},
      {id: 5, submission: genSubmission()},
      {id: 6, submission: genSubmission()},
    ]
    submissions[1].submission.id = 2
    submissions[2].submission.id = 3
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    // @ts-ignore
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {count: 3, size: 10}
    await wrapper.vm.$nextTick()
    expect(vm.compare).toBe(1)
  })
  it('Falls back to normal value comparison when comparison override is not specified', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        localVue,
        store,
        propsData: {
          value: 2, queryEndpoint: '/stuff/',
        },
        sync: false,
        attachToDocument: true,
        stubs: ['router-link'],
      }
    )
    const vm = wrapper.vm as any
    const submissions = [genSubmission(), genSubmission(), genSubmission()]
    submissions[0].id = 1
    submissions[1].id = 2
    submissions[2].id = 3
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {count: 3, size: 10}
    await wrapper.vm.$nextTick()
    expect(vm.compare).toBe(2)
  })
  it('Selects a submission', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        localVue,
        store,
        propsData: {
          value: 1, queryEndpoint: '/stuff/', saveComparison: currentSubmission,
        },
        sync: false,
        attachToDocument: true,
        stubs: ['router-link'],
      }
    )
    const vm = wrapper.vm as any
    const submissions = [genSubmission(), genSubmission(), genSubmission()]
    submissions[0].id = 2
    submissions[1].id = 3
    submissions[2].id = 4
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {count: 3, size: 10}
    await wrapper.vm.$nextTick()
    expect(vm.compare).toBe(1)
    const mockEmit = jest.spyOn(wrapper.vm, '$emit')
    expect(vm.loading).toBe(false)
    wrapper.find('.submission').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockEmit).toHaveBeenCalledWith('input', 2)
    expect(vm.loading).toBe(2)
  })
  it('Resets the loading marker as needed', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        localVue,
        store,
        propsData: {
          value: 1, queryEndpoint: '/stuff/', saveComparison: currentSubmission,
        },
        sync: false,
        attachToDocument: true,
        stubs: ['router-link'],
      }
    )
    const vm = wrapper.vm as any
    const submissions = [genSubmission(), genSubmission(), genSubmission()]
    submissions[0].id = 2
    submissions[1].id = 3
    submissions[2].id = 4
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {count: 3, size: 10}
    await wrapper.vm.$nextTick()
    wrapper.find('.submission').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.setProps({
      value: 1, queryEndpoint: '/stuff/', saveComparison: submissions[0],
    })
    await wrapper.vm.$nextTick()
    expect(vm.loading).toBe(false)
  })
  it('Handles a late-coming list', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        localVue,
        store,
        propsData: {
          value: 1, saveComparison: currentSubmission,
        },
        sync: false,
        attachToDocument: true,
        stubs: ['router-link'],
      }
    )
    const vm = wrapper.vm as any
    const submissions = [genSubmission(), genSubmission(), genSubmission()]
    const submissionList = mount(Empty, {localVue, store}).vm.$getList('submissions', {endpoint: '/wat/'})
    submissions[0].id = 2
    submissions[1].id = 3
    submissions[2].id = 4
    submissionList.ready = true
    submissionList.fetching = false
    submissionList.setList(submissions)
    submissionList.response = {count: 3, size: 10}
    wrapper.setProps({list: submissionList})
    await wrapper.vm.$nextTick()
    wrapper.find('.submission').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.setProps({
      value: 1, queryEndpoint: '/stuff/', saveComparison: submissions[0],
    })
    await wrapper.vm.$nextTick()
    expect(vm.loading).toBe(false)
  })
  it('Does not mark as loading when selecting the selected item', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        localVue,
        store,
        propsData: {
          value: 1, queryEndpoint: '/stuff/', saveComparison: currentSubmission,
        },
        sync: false,
        attachToDocument: true,
        stubs: ['router-link'],
      }
    )
    const vm = wrapper.vm as any
    const submissions = [currentSubmission, genSubmission(), genSubmission()]
    submissions[1].id = 2
    submissions[2].id = 3
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {count: 3, size: 10}
    const mockEmit = jest.spyOn(wrapper.vm, '$emit')
    await wrapper.vm.$nextTick()
    wrapper.find('.submission').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockEmit).toHaveBeenCalledWith('input', 1)
    expect(vm.loading).toBe(false)
  })
})
