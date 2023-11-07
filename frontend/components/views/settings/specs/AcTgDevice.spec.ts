import {VueWrapper} from '@vue/test-utils'
import AcTgDevice from '../AcTgDevice.vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, flushPromises, mount, rq, setViewer, vueSetup, VuetifyWrapped} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {ListController} from '@/store/lists/controller'
import {TOTPDevice} from '@/store/profiles/types/TOTPDevice'
import mockAxios from '@/specs/helpers/mock-axios'
import Empty from '@/specs/helpers/dummy_components/empty'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

const qrImageUrl = 'otpauth://totp/Artconomy%20Dev%3Afox%40vulpinity.com?secret=KJZWLZLDMVY3XJAX72V4WAXDKKZZDA76' +
  '&algorithm=SHA1&digits=6&period=30&issuer=Artconomy+Dev'

const WrappedDevice = VuetifyWrapped(AcTgDevice)

describe('AcTgDevice.vue', () => {
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
      data: {},
    })
    await flushPromises()
    expect(controller.list).toEqual([])
  })
  test('Sends a telegram code', async() => {
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
    wrapper.vm.$refs.vm.step = 2
    await wrapper.vm.$nextTick()
    await wrapper.find('.send-tg-code').trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Fox/auth/two-factor/tg/', 'post', undefined, {}))
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
    wrapper.vm.$refs.vm.step = 3
    const form = wrapper.vm.$getForm('telegramOTP')
    form.fields.code.update('123456')
    await wrapper.vm.$nextTick()
    await wrapper.find('.submit-button').trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Fox/auth/two-factor/tg/', 'patch', {code: '123 456'}, {}))
  })
  test('Updates the form URL if the username changes', async() => {
    const user = genUser()
    user.username = 'Vulpes'
    setViewer(store, genUser())
    await store.dispatch('profiles/saveUser', user)
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
    const vm = wrapper.vm.$refs.vm
    expect(vm.url).toBe('/api/profiles/account/Fox/auth/two-factor/tg/')
    await wrapper.setProps({
      username: 'Vulpes',
      device: {...controller.list[0]},
    })
    await wrapper.vm.$nextTick()
    expect(vm.url).toBe('/api/profiles/account/Vulpes/auth/two-factor/tg/')
    expect(vm.form.endpoint).toBe('/api/profiles/account/Vulpes/auth/two-factor/tg/')
  })
})
