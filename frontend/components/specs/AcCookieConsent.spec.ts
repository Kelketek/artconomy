import {cleanUp, mount, vueSetup, VuetifyWrapped} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import AcCookieConsent from '@/components/AcCookieConsent.vue'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

const WrappedConsent = VuetifyWrapped(AcCookieConsent)

describe('AcCookieConsent.vue', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  window._drip = vi.fn()
  window._ga = vi.fn()
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Shows a snackbar when cookie settings are not set.', async() => {
    wrapper = mount(WrappedConsent, vueSetup({store}))
    expect(wrapper.find('.customize-cookies-button').exists()).toBe(true)
  })
  test('Does not show a snackbar when cookie settings are set.', async() => {
    localStorage.setItem('cookieOptionsSetV1', '1')
    wrapper = mount(WrappedConsent, vueSetup({store}))
    expect(wrapper.find('.customize-cookies-button').exists()).toBe(false)
  })
  test('Accepts all cookies.', async() => {
    wrapper = mount(WrappedConsent, vueSetup({store}))
    expect(localStorage.getItem('cookieOptionsSetV1')).toBe(null)
    expect(localStorage.getItem('firstPartyAnalytics')).toBe(null)
    expect(localStorage.getItem('thirdPartyAnalytics')).toBe(null)
    await wrapper.find('.accept-cookies-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(localStorage.getItem('cookieOptionsSetV1')).toBe('1')
    expect(localStorage.getItem('firstPartyAnalytics')).toBe('1')
    expect(localStorage.getItem('thirdPartyAnalytics')).toBe('1')
  })
  test('Shows a dialog, hiding the snackbar while it is active.', async() => {
    wrapper = mount(WrappedConsent, vueSetup({store}))
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.dialog-submit').exists()).toBe(false)
    await wrapper.find('.customize-cookies-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.customize-cookies-button').exists()).toBe(false)
    expect(wrapper.find('.dialog-submit').exists()).toBe(true)
  })
  test('Enables only essential cookies.', async() => {
    wrapper = mount(WrappedConsent, vueSetup({store}))
    await wrapper.vm.$nextTick()
    await wrapper.find('.customize-cookies-button').trigger('click')
    await wrapper.vm.$nextTick()
    await wrapper.find('.essential-cookies-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.customize-cookies-button').exists()).toBe(false)
    expect(localStorage.getItem('cookieOptionsSetV1')).toBe('1')
    expect(localStorage.getItem('firstPartyAnalytics')).toBe('0')
    expect(localStorage.getItem('thirdPartyAnalytics')).toBe('0')
    expect(store.state.showCookieDialog).toBe(false)
  })
  test('Saves specific cookies.', async() => {
    wrapper = mount(WrappedConsent, vueSetup({store}))
    await wrapper.vm.$nextTick()
    await wrapper.find('.customize-cookies-button').trigger('click')
    await wrapper.vm.$nextTick()
    await wrapper.find('.third-party-analytics input').trigger('click')
    await wrapper.vm.$nextTick()
    await wrapper.find('.dialog-submit').trigger('click')
    expect(wrapper.find('.customize-cookies-button').exists()).toBe(false)
    expect(localStorage.getItem('cookieOptionsSetV1')).toBe('1')
    expect(localStorage.getItem('firstPartyAnalytics')).toBe('1')
    expect(localStorage.getItem('thirdPartyAnalytics')).toBe('0')
    expect(store.state.showCookieDialog).toBe(false)
  })
})
