import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {searchSchema} from '@/lib/lib.ts'
import {
  cleanUp,
  flushPromises,
  mount,
  rq,
  rs,
  setPricing,
  setViewer,
  vueSetup,
  VuetifyWrapped,
  waitFor,
} from '@/specs/helpers/index.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {SingleController} from '@/store/singles/controller.ts'
import Product from '@/types/Product.ts'
import {ListController} from '@/store/lists/controller.ts'
import {genProduct, genUser} from '@/specs/helpers/fixtures.ts'
import Submission from '@/types/Submission.ts'
import AcSampleEditor from '@/components/views/product/AcSampleEditor.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import LinkedSubmission from '@/types/LinkedSubmission.ts'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let form: FormController
let product: SingleController<Product>
let samplesList: ListController<LinkedSubmission>
let localSamples: ListController<LinkedSubmission>
let art: ListController<Submission>

const WrappedEditor = VuetifyWrapped(AcSampleEditor)

describe('AcSampleEditor.vue', () => {
  beforeEach(() => {
    store = createStore()
    const empty = mount(Empty, vueSetup({store})).vm
    form = empty.$getForm('search', searchSchema())
    setPricing(store)
    product = empty.$getSingle('product', {endpoint: '/product/'})
    product.setX(genProduct())
    product.fetching = false
    product.ready = true
    samplesList = empty.$getList('product__1__samples', {endpoint: '/dude/'})
    samplesList.setList([])
    samplesList.fetching = false
    samplesList.ready = true
    localSamples = empty.$getList(`product-${(product.x as Product).id}-sample-select`, {endpoint: '/samples/'})
    localSamples.setList([])
    localSamples.ready = true
    localSamples.fetching = false
    art = empty.$getList('Fox-art', {endpoint: '/art/'})
    art.setList([])
    art.fetching = false
    art.ready = true
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Clears the showcased submission', async() => {
    setViewer(store, genUser())
    wrapper = mount(WrappedEditor, {
      ...vueSetup({
        store,
        stubs: ['ac-new-submission'],
      }),
      props: {
        product,
        productId: (product.x as Product).id,
        username: 'Fox',
        value: true,
        samples: samplesList,
      },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(product.patchers.primary_submission.model).not.toBeNull()
    mockAxios.reset()
    await wrapper.find('.clear-showcased').trigger('click')
    await wrapper.vm.$nextTick()
    const newVersion = {...product.x as Product}
    newVersion.primary_submission = null
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/product/', 'patch', {primary_submission: null}),
    )
    mockAxios.mockResponse(rs(newVersion))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(product.x!.primary_submission).toBeNull()
  })
  test('Clears the sample status of a submission', async() => {
    setViewer(store, genUser())
    const submission = {
      id: 1,
      submission: genSubmission(),
    }
    const submission2 = {
      id: 2,
      submission: genSubmission(),
    }
    const submission3 = {
      id: 3,
      submission: genSubmission(),
    }
    submission.submission.id = 5
    submission2.submission.id = 6
    submission3.submission.id = 7
    const samples = [submission, submission2, submission3]
    const response = {
      count: 3,
      size: 24,
    }
    samplesList.setList([...samples])
    localSamples.setList([...samples])
    samplesList.response = response
    localSamples.response = response
    wrapper = mount(AcSampleEditor, {
      ...vueSetup({
        store,
        stubs: ['ac-new-submission', 'router-link'],
      }),
      props: {
        product,
        productId: (product.x as Product).id,
        username: 'Fox',
        value: true,
        samples: samplesList,
      },
    })
    await wrapper.vm.$nextTick()
    await wrapper.find('.remove-submission').trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/samples/1/', 'delete', undefined))
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(samplesList.list.length).toBe(2)
    expect(localSamples.list.length).toBe(2)
  })
  test('Clears the sample status of the primary submission', async() => {
    setViewer(store, genUser())
    const submission = {
      id: 1,
      submission: genSubmission(),
    }
    const submission2 = {
      id: 2,
      submission: genSubmission(),
    }
    const submission3 = {
      id: 3,
      submission: genSubmission(),
    }
    submission.submission.id = 5
    submission2.submission.id = 6
    submission3.submission.id = 7
    const samples = [submission, submission2, submission3]
    const response = {
      count: 3,
      size: 24,
    }
    samplesList.setList([...samples])
    localSamples.setList([...samples])
    samplesList.response = response
    localSamples.response = response
    product.updateX({primary_submission: submission.submission})
    wrapper = mount(AcSampleEditor, {
      ...vueSetup({
        store,
        stubs: ['ac-new-submission', 'router-link'],
      }),
      props: {
        product,
        productId: (product.x as Product).id,
        username: 'Fox',
        value: true,
        samples: samplesList,
      },
    })
    await wrapper.vm.$nextTick()
    await wrapper.find('.remove-submission').trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/samples/1/', 'delete', undefined))
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect((product.x as Product).primary_submission).toBeNull()
    expect(samplesList.list.length).toBe(2)
    expect(localSamples.list.length).toBe(2)
  })
  test('Turns an art submission into a sample', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    const submission2 = genSubmission()
    const submission3 = genSubmission()
    submission.id = 5
    submission2.id = 6
    submission3.id = 7
    const samples = [submission, submission2, submission3]
    art.response = {
      count: 3,
      size: 24,
    }
    art.setList(samples)
    wrapper = mount(AcSampleEditor, {
      ...vueSetup({
        store,
        stubs: ['ac-new-submission', 'router-link'],
      }),
      props: {
        product,
        productId: (product.x as Product).id,
        username: 'Fox',
        value: true,
        samples: samplesList,
      },
    })
    await wrapper.vm.$nextTick()
    mockAxios.reset()
    const vm = wrapper.vm as any
    await wrapper.find('.product-sample-option').trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/samples/', 'post', {submission_id: 5}))
    mockAxios.mockResponse(rs({
      id: 1,
      submission,
    }))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(samplesList.list.length).toBe(1)
    expect(localSamples.list.length).toBe(1)
  })
  test('Turns an art submission into a sample and sets the primary submission', async() => {
    setViewer(store, genUser())
    product.updateX({primary_submission: null})
    const submission = genSubmission()
    const submission2 = genSubmission()
    const submission3 = genSubmission()
    submission.id = 5
    submission2.id = 6
    submission3.id = 7
    const samples = [submission, submission2, submission3]
    art.response = {
      count: 3,
      size: 24,
    }
    art.setList(samples)
    wrapper = mount(AcSampleEditor, {
      ...vueSetup({
        store,
        stubs: ['ac-new-submission', 'router-link'],
      }),
      props: {
        product,
        productId: (product.x as Product).id,
        username: 'Fox',
        value: true,
        samples: samplesList,
      },
    })
    await wrapper.vm.$nextTick()
    mockAxios.reset()
    await wrapper.find('.product-sample-option').trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/samples/', 'post', {submission_id: 5}))
    mockAxios.mockResponse(rs({
      id: 1,
      submission,
    }))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/product/', 'patch', {primary_submission: 5}))
    mockAxios.mockResponse(rs({...product.x, ...{primary_submission: submission}}))
    expect(samplesList.list.length).toBe(1)
    expect(localSamples.list.length).toBe(1)
    expect((product.x as Product).primary_submission).toBeTruthy()
  })
  test('Adds a new sample', async() => {
    setViewer(store, genUser())
    wrapper = mount(AcSampleEditor, {
      ...vueSetup({
        store,
        stubs: ['ac-new-submission', 'router-link'],
      }),
      props: {
        product,
        productId: (product.x as Product).id,
        username: 'Fox',
        value: true,
        samples: samplesList,
      },
    })
    const vm = wrapper.vm as any
    await wrapper.vm.$nextTick()
    const submission = genSubmission()
    submission.id = 1337
    mockAxios.reset()
    vm.addSample(submission)
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/samples/', 'post', {submission_id: 1337}))
    mockAxios.mockResponse(rs({
      id: 1,
      submission,
    }))
    await flushPromises()
    await vm.$nextTick()
    expect(localSamples.list.length).toBe(1)
    expect(samplesList.list.length).toBe(1)
  })
  test('Adds a new sample and sets the primary submission', async() => {
    setViewer(store, genUser())
    product.updateX({primary_submission: null})
    wrapper = mount(AcSampleEditor, {
      ...vueSetup({
        store,
        stubs: ['ac-new-submission', 'router-link'],
      }),
      props: {
        product,
        productId: (product.x as Product).id,
        username: 'Fox',
        value: true,
        samples: samplesList,
      },
    })
    const vm = wrapper.vm as any
    await wrapper.vm.$nextTick()
    const submission = genSubmission()
    submission.id = 1337
    mockAxios.reset()
    vm.addSample(submission)
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/samples/', 'post', {submission_id: 1337}))
    mockAxios.mockResponse(rs({
      id: 1,
      submission,
    }))
    await flushPromises()
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/product/', 'patch', {primary_submission: 1337}),
    )
    mockAxios.mockResponse(rs({...product.x, ...{primary_submission: submission}}))
    await flushPromises()
    await vm.$nextTick()
    expect(localSamples.list.length).toBe(1)
    expect(samplesList.list.length).toBe(1)
  })
  test('Toggles', async() => {
    setViewer(store, genUser())
    wrapper = mount(AcSampleEditor, {
      ...vueSetup({
        store,
        stubs: ['ac-new-submission', 'router-link'],
      }),
      props: {
        product,
        productId: (product.x as Product).id,
        username: 'Fox',
        value: true,
        samples: samplesList,
      },
    })
    await wrapper.vm.$nextTick()
    await wrapper.find('.dialog-closer').trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()
    console.log(wrapper.emitted())
    expect(wrapper.emitted('update:modelValue')![0])
  })
})
