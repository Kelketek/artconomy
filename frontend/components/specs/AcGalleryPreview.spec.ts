import {shallowMount, VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {cleanUp, genAnon, setViewer, vueSetup} from '@/specs/helpers'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('AcGalleryPreview.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Displays a preview of a submission', async() => {
    setViewer(store, genAnon())
    const submission = genSubmission()
    submission.id = 534
    wrapper = shallowMount(AcGalleryPreview, {
      ...vueSetup({stubs: ['router-link']}),
      props: {submission},
    })
    const vm = wrapper.vm as any
    expect(vm.submissionLink).toEqual({
      name: 'Submission',
      params: {submissionId: 534},
    })
  })
})
