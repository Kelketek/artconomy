import {VueWrapper} from '@vue/test-utils'
import PrivacyPolicy from '../PrivacyPolicy.vue'
import RefundPolicy from '../RefundPolicy.vue'
import CommissionAgreement from '../CommissionAgreement.vue'
import TermsOfService from '../TermsOfService.vue'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {afterEach, describe, expect, test} from 'vitest'

let wrapper: VueWrapper<any>

describe('Legal Pages', () => {
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Renders the privacy policy', async() => {
    wrapper = mount(PrivacyPolicy, vueSetup({stubs: ['router-link']}))
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
  test('Renders the refund policy', async() => {
    wrapper = mount(RefundPolicy, vueSetup({stubs: ['router-link']}))
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
  test('Renders the commission agreement', async() => {
    wrapper = mount(CommissionAgreement, vueSetup({stubs: ['router-link']}))
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
  test('Renders the terms of service', async() => {
    wrapper = mount(TermsOfService, vueSetup({stubs: ['router-link']}))
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
})
