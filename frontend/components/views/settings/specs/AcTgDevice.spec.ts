import {mount, Wrapper} from '@vue/test-utils'
import AcTgDevice from '../AcTgDevice.vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, flushPromises, rq, setViewer, vueSetup} from '@/specs/helpers'
import Vue from 'vue'
import {genUser} from '@/specs/helpers/fixtures'
import {ListController} from '@/store/lists/controller'
import {TOTPDevice} from '@/store/profiles/types/TOTPDevice'
import {Vuetify} from 'vuetify/types'
import mockAxios from '@/specs/helpers/mock-axios'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const qrImageUrl = 'otpauth://totp/Artconomy%20Dev%3Afox%40vulpinity.com?secret=KJZWLZLDMVY3XJAX72V4WAXDKKZZDA76' +
  '&algorithm=SHA1&digits=6&period=30&issuer=Artconomy+Dev'

describe('AcTgDevice.vue', () => {
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
    wrapper = mount(AcTgDevice, {
      store,
      localVue,
      vuetify,
      propsData: {username: 'Fox', device: controller.list[0]},
      sync: false,
    })
    expect(wrapper.findAll('.v-stepper__step').length).toBe(3)
  })
  it('Shows no steps if the device is confirmed', async() => {
    setViewer(store, genUser())
    controller.setList([{id: 1, confirmed: true, config_url: qrImageUrl, name: 'Phone'}])
    wrapper = mount(AcTgDevice, {
      store,
      localVue,
      vuetify,
      propsData: {username: 'Fox', device: controller.list[0]},
      sync: false,
    })
    expect(wrapper.findAll('.v-stepper__step').length).toBe(0)
  })
  it('Deletes a device', async() => {
    setViewer(store, genUser())
    controller.setList([{id: 1, confirmed: true, config_url: qrImageUrl, name: 'Phone'}])
    wrapper = mount(AcTgDevice, {
      store,
      localVue,
      vuetify,
      propsData: {username: 'Fox', device: controller.list[0]},
      sync: false,
    })
    mockAxios.reset()
    wrapper.find('.delete-phone-2fa').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('.confirmation-button').trigger('click')
    expect(mockAxios.delete).toHaveBeenCalledWith(
      ...rq('/test/1/', 'delete')
    )
    mockAxios.mockResponse({status: 204, data: {}})
    await flushPromises()
    expect(controller.list).toEqual([])
  })
  it('Sends a telegram code', async() => {
    setViewer(store, genUser())
    mockError.mockImplementationOnce(() => undefined)
    controller.setList([{id: 1, confirmed: false, config_url: qrImageUrl, name: 'Phone'}])
    wrapper = mount(AcTgDevice, {
      store,
      localVue,
      vuetify,
      propsData: {username: 'Fox', device: controller.list[0]},
      sync: false,
      attachToDocument: true,
    })
    wrapper.find('.send-tg-code').trigger('click')
    expect(mockAxios.post).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/auth/two-factor/tg/', 'post', undefined, {}))
  })
  it('Sends a verification code', async() => {
    setViewer(store, genUser())
    mockError.mockImplementationOnce(() => undefined)
    controller.setList([{id: 1, confirmed: false, config_url: qrImageUrl, name: 'Phone'}])
    wrapper = mount(AcTgDevice, {
      store,
      localVue,
      vuetify,
      propsData: {username: 'Fox', device: controller.list[0]},
      sync: false,
      attachToDocument: true,
    })
    const form = wrapper.vm.$getForm('telegramOTP')
    form.fields.code.update('123456')
    wrapper.find('.submit-button').trigger('click')
    expect(mockAxios.patch).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/auth/two-factor/tg/', 'patch', {code: '123456'}, {}))
  })
  it('Updates the form URL if the username changes', async() => {
    const user = genUser()
    user.username = 'Vulpes'
    setViewer(store, genUser())
    await store.dispatch('profiles/saveUser', user)
    controller.setList([{id: 1, confirmed: true, config_url: qrImageUrl, name: 'Phone'}])
    wrapper = mount(AcTgDevice, {
      store,
      localVue,
      vuetify,
      propsData: {username: 'Fox', device: controller.list[0]},
      sync: false,
    })
    expect((wrapper.vm as any).url).toBe('/api/profiles/v1/account/Fox/auth/two-factor/tg/')
    wrapper.setProps({username: 'Vulpes', device: {...controller.list[0]}})
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).url).toBe('/api/profiles/v1/account/Vulpes/auth/two-factor/tg/')
    expect((wrapper.vm as any).form.endpoint).toBe('/api/profiles/v1/account/Vulpes/auth/two-factor/tg/')
  })
})
