import {shallowMount, VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, vueSetup} from '@/specs/helpers/index.ts'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'
import {setViewer} from '@/lib/lib.ts'
import {genAnon} from '@/specs/helpers/fixtures.ts'

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
    setViewer({ store, user: genAnon() })
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
