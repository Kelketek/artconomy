import {mount, Wrapper} from '@vue/test-utils'
import AcTotpDevice from '../AcTotpDevice.vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, docTarget, flushPromises, rq, setViewer, vueSetup} from '@/specs/helpers'
import Vue from 'vue'
import {genUser} from '@/specs/helpers/fixtures'
import {ListController} from '@/store/lists/controller'
import {TOTPDevice} from '@/store/profiles/types/TOTPDevice'
import mockAxios from '@/specs/helpers/mock-axios'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {Vuetify} from 'vuetify'

const qrImageUrl = 'otpauth://totp/Artconomy%20Dev%3Afox%40vulpinity.com?secret=KJZWLZLDMVY3XJAX72V4WAXDKKZZDA76' +
  '&algorithm=SHA1&digits=6&period=30&issuer=Artconomy+Dev'

describe('AcTotpDevice.vue', () => {
  const mockError = jest.spyOn(console, 'error')
  const localVue = vueSetup()
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  let controller: ListController<TOTPDevice>
  let vuetify: Vuetify
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    controller = mount(Empty, {localVue, store}).vm.$getList('totpDevices', {endpoint: '/test/'})
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Shows a set of steps', async() => {
    setViewer(store, genUser())
    controller.setList([{id: 1, confirmed: false, config_url: qrImageUrl, name: 'Phone'}])
    wrapper = mount(AcTotpDevice, {
      store,
      localVue,
      vuetify,
      propsData: {username: 'Fox', device: controller.list[0]},

    })
    expect(wrapper.findAll('.v-stepper__step').length).toBe(3)
  })
  it('Shows no steps if the device is confirmed', async() => {
    setViewer(store, genUser())
    controller.setList([{id: 1, confirmed: true, config_url: qrImageUrl, name: 'Phone'}])
    wrapper = mount(AcTotpDevice, {
      store,
      localVue,
      vuetify,
      propsData: {username: 'Fox', device: controller.list[0]},

    })
    expect(wrapper.findAll('.v-stepper__step').length).toBe(0)
  })
  it('Deletes a device', async() => {
    setViewer(store, genUser())
    controller.setList([{id: 1, confirmed: true, config_url: qrImageUrl, name: 'Phone'}])
    wrapper = mount(AcTotpDevice, {
      store,
      localVue,
      vuetify,
      propsData: {username: 'Fox', device: controller.list[0]},

    })
    mockAxios.reset()
    wrapper.find('.delete-phone-2fa').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('.confirmation-button').trigger('click')
    expect(mockAxios.delete).toHaveBeenCalledWith(
      ...rq('/test/1/', 'delete'),
    )
    mockAxios.mockResponse({status: 204, data: null})
    await flushPromises()
    expect(controller.list).toEqual([])
  })
  it('Logs an error if there was an issue building the QR code image', async() => {
    setViewer(store, genUser())
    mockError.mockImplementationOnce(() => undefined)
    controller.setList([{id: 1, confirmed: false, config_url: '', name: 'Phone'}])
    wrapper = mount(AcTotpDevice, {
      store,
      localVue,
      vuetify,
      propsData: {username: 'Fox', device: controller.list[0]},

    })
    expect(mockError).toHaveBeenCalledWith(Error('No input text'))
  })
  it('Sends a verification code', async() => {
    setViewer(store, genUser())
    mockError.mockImplementationOnce(() => undefined)
    controller.setList([{id: 1, confirmed: false, config_url: qrImageUrl, name: 'Phone'}])
    wrapper = mount(AcTotpDevice, {
      store,
      localVue,
      vuetify,
      propsData: {username: 'Fox', device: controller.list[0]},

      attachTo: docTarget(),
    })
    const form = wrapper.vm.$getForm('1_totpForm')
    form.fields.code.update('123456')
    wrapper.find('.submit-button').trigger('click')
    expect(mockAxios.patch).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/auth/two-factor/totp/1/', 'patch', {code: '123456'}, {}))
  })
})
