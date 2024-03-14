import {cleanUp, createTestRouter, mount, vueSetup} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import AcReference from '@/components/views/order/deliverable/AcReference.vue'
import {genReference} from '@/specs/helpers/fixtures.ts'
import {afterEach, beforeAll, describe, expect, MockedFunction, test, vi} from 'vitest'
import {Router} from 'vue-router'

let wrapper: VueWrapper<any>
let mockOpen: MockedFunction<any>
let router: Router

describe('AcReference.vue', () => {
  beforeAll(() => {
    mockOpen = vi.fn()
    window.open = mockOpen
    router = createTestRouter(false)
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
        extraPlugins: [router],
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
