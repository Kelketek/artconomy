import FormContainer from '@/specs/helpers/dummy_components/form-container.vue'
import {AxiosError} from 'axios'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {VueWrapper} from '@vue/test-utils'

const mockTrace = vi.spyOn(console, 'trace')

describe('AcFormContainer.vue', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Sets default properties', async() => {
    // Needed for that last bit of code coverage.
    wrapper = mount(FormContainer, vueSetup({store}))
    expect((wrapper.vm as any).$refs.defaultForm.errors).toEqual([])
    expect((wrapper.vm as any).$refs.defaultForm.sending).toEqual(false)
  })
  test('Displays dismissible errors', async() => {
    wrapper = mount(FormContainer, vueSetup({store}))
    const vm = wrapper.vm as any
    mockTrace.mockImplementationOnce(() => undefined)
    vm.basicForm.setErrors({} as AxiosError)
    await vm.$nextTick()
    await wrapper.find('.v-alert__close button').trigger('click')
    await vm.$nextTick()
  })
})
