import {createLocalVue, shallowMount} from '@vue/test-utils'
import PrivacyPolicy from '../PrivacyPolicy.vue'
import RefundPolicy from '../RefundPolicy.vue'
import CommissionAgreement from '../CommissionAgreement.vue'
import TermsOfService from '../TermsOfService.vue'
import VueRouter from 'vue-router'

const localVue = createLocalVue()
localVue.use(VueRouter)

describe('Legal Pages', () => {
  it('Renders the privacy policy', () => {
    const wrapper = shallowMount(PrivacyPolicy, {localVue})
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
  it('Renders the refund policy', () => {
    const wrapper = shallowMount(RefundPolicy, {localVue})
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
  it('Renders the commission agreement', () => {
    const wrapper = shallowMount(CommissionAgreement, {localVue})
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
  it('Renders the terms of service', () => {
    const wrapper = shallowMount(TermsOfService, {localVue})
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
})
