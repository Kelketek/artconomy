import {VueWrapper} from '@vue/test-utils'
import {cleanUp, genAnon, mount, setViewer, vueSetup} from '@/specs/helpers'
import AcSubmissionSelect from '@/components/fields/AcSubmissionSelect.vue'
import {ArtStore, createStore} from '@/store'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
vi.useFakeTimers()
let wrapper: VueWrapper<any>

describe('AcSubmissionSelect.vue', () => {
  beforeEach(() => {
    store = createStore()
    setViewer(store, genAnon())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Gets the right comparison ID when comparison is specified', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {
          modelValue: 2,
          queryEndpoint: '/stuff/',
          saveComparison: currentSubmission,
        },
      },
    )
    const vm = wrapper.vm as any
    const submissions = [currentSubmission, genSubmission(), genSubmission()]
    submissions[1].id = 2
    submissions[2].id = 3
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {
      count: 3,
      size: 10,
    }
    await wrapper.vm.$nextTick()
    expect(vm.compare).toBe(1)
  })
  test('Gets the right comparison ID when comparison is specified and the related switch is enabled', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {
          modelValue: 2,
          queryEndpoint: '/stuff/',
          saveComparison: currentSubmission,
          related: true,
        },
      },
    )
    const vm = wrapper.vm as any
    const submissions = [
      {
        id: 4,
        submission: currentSubmission,
      },
      {
        id: 5,
        submission: genSubmission(),
      },
      {
        id: 6,
        submission: genSubmission(),
      },
    ]
    submissions[1].submission.id = 2
    submissions[2].submission.id = 3
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    // @ts-ignore
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {
      count: 3,
      size: 10,
    }
    await wrapper.vm.$nextTick()
    expect(vm.compare).toBe(1)
  })
  test('Falls back to normal value comparison when comparison override is not specified', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {
          modelValue: 2,
          queryEndpoint: '/stuff/',
        },
      },
    )
    const vm = wrapper.vm as any
    const submissions = [genSubmission(), genSubmission(), genSubmission()]
    submissions[0].id = 1
    submissions[1].id = 2
    submissions[2].id = 3
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {
      count: 3,
      size: 10,
    }
    await wrapper.vm.$nextTick()
    expect(vm.compare).toBe(2)
  })
  test('Selects a submission', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {
          modelValue: 1,
          queryEndpoint: '/stuff/',
          saveComparison: currentSubmission,
        },
      },
    )
    const vm = wrapper.vm as any
    const submissions = [genSubmission(), genSubmission(), genSubmission()]
    submissions[0].id = 2
    submissions[1].id = 3
    submissions[2].id = 4
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {
      count: 3,
      size: 10,
    }
    await wrapper.vm.$nextTick()
    expect(vm.compare).toBe(1)
    expect(vm.loading).toBe(false)
    await wrapper.find('.submission').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([2])
    expect(vm.loading).toBe(2)
  })
  test('Resets the loading marker as needed', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {
          modelValue: 1,
          queryEndpoint: '/stuff/',
          saveComparison: currentSubmission,
        },
      },
    )
    const vm = wrapper.vm as any
    const submissions = [genSubmission(), genSubmission(), genSubmission()]
    submissions[0].id = 2
    submissions[1].id = 3
    submissions[2].id = 4
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {
      count: 3,
      size: 10,
    }
    await wrapper.vm.$nextTick()
    await wrapper.find('.submission').trigger('click')
    await wrapper.vm.$nextTick()
    await wrapper.setProps({
      value: 1,
      queryEndpoint: '/stuff/',
      saveComparison: submissions[0],
    })
    await wrapper.vm.$nextTick()
    expect(vm.loading).toBe(false)
  })
  test('Handles a late-coming list', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {
          modelValue: 1,
          saveComparison: currentSubmission,
        },
      },
    )
    const vm = wrapper.vm as any
    const submissions = [genSubmission(), genSubmission(), genSubmission()]
    const submissionList = mount(Empty, vueSetup({store})).vm.$getList('submissions', {endpoint: '/wat/'})
    submissions[0].id = 2
    submissions[1].id = 3
    submissions[2].id = 4
    submissionList.ready = true
    submissionList.fetching = false
    submissionList.setList(submissions)
    submissionList.response = {
      count: 3,
      size: 10,
    }
    await wrapper.setProps({list: submissionList})
    await wrapper.vm.$nextTick()
    await wrapper.find('.submission').trigger('click')
    await wrapper.vm.$nextTick()
    await wrapper.setProps({
      value: 1,
      queryEndpoint: '/stuff/',
      saveComparison: submissions[0],
    })
    await wrapper.vm.$nextTick()
    expect(vm.loading).toBe(false)
  })
  test('Does not mark as loading when selecting the selected item', async() => {
    const currentSubmission = genSubmission()
    currentSubmission.id = 1
    wrapper = mount(
      AcSubmissionSelect, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {
          modelValue: 1,
          queryEndpoint: '/stuff/',
          saveComparison: currentSubmission,
        },
      },
    )
    const vm = wrapper.vm as any
    const submissions = [currentSubmission, genSubmission(), genSubmission()]
    submissions[1].id = 2
    submissions[2].id = 3
    vm.submissionList.ready = true
    vm.submissionList.fetching = false
    vm.submissionList.setList(submissions)
    vm.submissionList.response = {
      count: 3,
      size: 10,
    }
    await wrapper.vm.$nextTick()
    await wrapper.find('.submission').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([1])
    expect(vm.loading).toBe(false)
  })
})
