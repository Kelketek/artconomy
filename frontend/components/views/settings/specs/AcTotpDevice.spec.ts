import {VueWrapper} from '@vue/test-utils'
import AcTotpDevice from '../AcTotpDevice.vue'
import {ArtStore, createStore} from '@/store'
import {
  cleanUp,
  createVuetify,
  docTarget,
  flushPromises,
  mount,
  rq,
  setViewer,
  vueSetup,
  VuetifyWrapped,
} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {ListController} from '@/store/lists/controller'
import {TOTPDevice} from '@/store/profiles/types/TOTPDevice'
import mockAxios from '@/specs/helpers/mock-axios'
import Empty from '@/specs/helpers/dummy_components/empty'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

const qrImageUrl = 'otpauth://totp/Artconomy%20Dev%3Afox%40vulpinity.com?secret=KJZWLZLDMVY3XJAX72V4WAXDKKZZDA76' +
  '&algorithm=SHA1&digits=6&period=30&issuer=Artconomy+Dev'

const WrappedDevice = VuetifyWrapped(AcTotpDevice)

describe('AcTotpDevice.vue', () => {
  const mockError = vi.spyOn(console, 'error')
  let store: ArtStore
  let wrapper: VueWrapper<any>
  let controller: ListController<TOTPDevice>
  beforeEach(() => {
    store = createStore()
    controller = mount(Empty, vueSetup({store})).vm.$getList('totpDevices', {endpoint: '/test/'})
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Shows a set of steps', async() => {
    setViewer(store, genUser())
    controller.setList([{
      id: 1,
      confirmed: false,
      config_url: qrImageUrl,
      name: 'Phone',
    }])
    wrapper = mount(WrappedDevice, {
      ...vueSetup({store}),
      props: {
        username: 'Fox',
        device: controller.list[0],
      },
    })
    expect(wrapper.findAll('.v-stepper-window-item').length).toBe(3)
  })
  test('Shows no steps if the device is confirmed', async() => {
    setViewer(store, genUser())
    controller.setList([{
      id: 1,
      confirmed: true,
      config_url: qrImageUrl,
      name: 'Phone',
    }])
    wrapper = mount(WrappedDevice, {
      ...vueSetup({store}),
      props: {
        username: 'Fox',
        device: controller.list[0],
      },
    })
    expect(wrapper.findAll('.v-stepper__step').length).toBe(0)
  })
  test('Deletes a device', async() => {
    setViewer(store, genUser())
    controller.setList([{
      id: 1,
      confirmed: true,
      config_url: qrImageUrl,
      name: 'Phone',
    }])
    wrapper = mount(WrappedDevice, {
      ...vueSetup({store}),
      props: {
        username: 'Fox',
        device: controller.list[0],
      },
    })
    mockAxios.reset()
    await wrapper.find('.delete-phone-2fa').trigger('click')
    await wrapper.vm.$nextTick()
    await wrapper.find('.confirmation-button').trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/test/1/', 'delete'),
    )
    mockAxios.mockResponse({
      status: 204,
      data: null,
    })
    await flushPromises()
    expect(controller.list).toEqual([])
  })
  test('Logs an error if there was an issue building the QR code image', async() => {
    setViewer(store, genUser())
    mockError.mockImplementationOnce(() => undefined)
    controller.setList([{
      id: 1,
      confirmed: false,
      config_url: '',
      name: 'Phone',
    }])
    wrapper = mount(WrappedDevice, {
      ...vueSetup({store}),
      props: {
        username: 'Fox',
        device: controller.list[0],
      },
    })
    expect(mockError).toHaveBeenCalledWith(Error('No input text'))
  })
  test('Sends a verification code', async() => {
    setViewer(store, genUser())
    mockError.mockImplementationOnce(() => undefined)
    controller.setList([{
      id: 1,
      confirmed: false,
      config_url: qrImageUrl,
      name: 'Phone',
    }])
    wrapper = mount(WrappedDevice, {
      ...vueSetup({store}),
      props: {
        username: 'Fox',
        device: controller.list[0],
      },
    })
    const form = wrapper.vm.$getForm('1_totpForm')
    form.fields.code.update('123456')
    wrapper.vm.$refs.vm.step = 3
    await wrapper.vm.$nextTick()
    await wrapper.find('.submit-button').trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Fox/auth/two-factor/totp/1/', 'patch', {code: '123 456'}, {}))
  })
})
