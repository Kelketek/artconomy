import {cleanUp, mount, vueSetup} from '@/specs/helpers'
import {VueWrapper} from '@vue/test-utils'
import AcReference from '@/components/views/order/deliverable/AcReference.vue'
import {genReference} from '@/specs/helpers/fixtures'
import {afterEach, beforeAll, describe, expect, MockedFunction, test, vi} from 'vitest'

let wrapper: VueWrapper<any>
let mockOpen: MockedFunction<any>

describe('AcReference.vue', () => {
  beforeAll(() => {
    mockOpen = vi.fn()
    window.open = mockOpen
  })
  afterEach(() => {
    cleanUp(wrapper)
    mockOpen.mockReset()
  })
  test('Pops into a new window', async() => {
    const reference = genReference()
    reference.file.full = 'https://example.com/stuff.jpg'
    const mockOpen = vi.spyOn(window, 'open')
    wrapper = mount(AcReference, {
      ...vueSetup({
        stubs: ['router-link'],
        mocks: {$route: {params: {}}},
      }),
      props: {
        reference,
        baseName: 'Sales',
      },
      stubs: ['router-link'],
      mocks: {$route: {params: {}}},
    })
    const vm = wrapper.vm as any
    await wrapper.find('.pop-out-button').trigger('click')
    await vm.$nextTick()
    expect(mockOpen).toHaveBeenCalledWith('https://example.com/stuff.jpg', '_blank')
  })
})
