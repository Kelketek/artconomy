import {cleanUp, createVuetify, docTarget, mount, vueSetup} from '@/specs/helpers'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import AcCookieConsent from '@/components/AcCookieConsent.vue'

describe('AcCookieConsent.vue', () => {
  const localVue = vueSetup()
  let vuetify: Vuetify
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Shows a snackbar when cookie settings are not set.', async() => {
    wrapper = mount(AcCookieConsent, {localVue, vuetify, store})
    expect(wrapper.find('.customize-cookies-button').exists()).toBe(true)
  })
  it('Does not show a snackbar when cookie settings are set.', async() => {
    localStorage.setItem('cookieOptionsSetV1', '1')
    wrapper = mount(AcCookieConsent, {localVue, vuetify, store})
    expect(wrapper.find('.customize-cookies-button').exists()).toBe(false)
  })
  it('Accepts all cookies.', async() => {
    wrapper = mount(AcCookieConsent, {localVue, vuetify, store})
    expect(localStorage.getItem('cookieOptionsSetV1')).toBe(null)
    expect(localStorage.getItem('firstPartyAnalytics')).toBe(null)
    expect(localStorage.getItem('thirdPartyAnalytics')).toBe(null)
    wrapper.find('.accept-cookies-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(localStorage.getItem('cookieOptionsSetV1')).toBe('1')
    expect(localStorage.getItem('firstPartyAnalytics')).toBe('1')
    expect(localStorage.getItem('thirdPartyAnalytics')).toBe('1')
  })
  it('Shows a dialog, hiding the snackbar while it is active.', async() => {
    wrapper = mount(AcCookieConsent, {localVue, vuetify, store, attachTo: docTarget()})
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.dialog-submit').exists()).toBe(false)
    wrapper.find('.customize-cookies-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.customize-cookies-button').exists()).toBe(false)
    expect(wrapper.find('.dialog-submit').exists()).toBe(true)
  })
  it('Enables only essential cookies.', async() => {
    wrapper = mount(AcCookieConsent, {localVue, vuetify, store, attachTo: docTarget()})
    await wrapper.vm.$nextTick()
    wrapper.find('.customize-cookies-button').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('.essential-cookies-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.customize-cookies-button').exists()).toBe(false)
    expect(localStorage.getItem('cookieOptionsSetV1')).toBe('1')
    expect(localStorage.getItem('firstPartyAnalytics')).toBe('0')
    expect(localStorage.getItem('thirdPartyAnalytics')).toBe('0')
    expect(store.state.showCookieDialog).toBe(false)
  })
  it('Saves specific cookies.', async() => {
    wrapper = mount(AcCookieConsent, {localVue, vuetify, store, attachTo: docTarget()})
    await wrapper.vm.$nextTick()
    wrapper.find('.customize-cookies-button').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('.third-party-analytics input').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('.dialog-submit').trigger('click')
    expect(wrapper.find('.customize-cookies-button').exists()).toBe(false)
    expect(localStorage.getItem('cookieOptionsSetV1')).toBe('1')
    expect(localStorage.getItem('firstPartyAnalytics')).toBe('1')
    expect(localStorage.getItem('thirdPartyAnalytics')).toBe('0')
    expect(store.state.showCookieDialog).toBe(false)
  })
})
