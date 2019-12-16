import Vue from 'vue'
import {Vuetify} from 'vuetify/types'
import {shallowMount, Wrapper} from '@vue/test-utils'
import PrivacyPolicy from '../PrivacyPolicy.vue'
import RefundPolicy from '../RefundPolicy.vue'
import CommissionAgreement from '../CommissionAgreement.vue'
import TermsOfService from '../TermsOfService.vue'
import VueRouter from 'vue-router'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'

const localVue = vueSetup()
localVue.use(VueRouter)
let vuetify: Vuetify
let wrapper: Wrapper<Vue>

describe('Legal Pages', () => {
  beforeEach(() => {
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Renders the privacy policy', async() => {
    wrapper = shallowMount(PrivacyPolicy, {localVue, vuetify, sync: false})
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
  it('Renders the refund policy', async() => {
    wrapper = shallowMount(RefundPolicy, {localVue, vuetify, sync: false})
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
  it('Renders the commission agreement', async() => {
    wrapper = shallowMount(CommissionAgreement, {localVue, vuetify, sync: false})
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
  it('Renders the terms of service', async() => {
    wrapper = shallowMount(TermsOfService, {localVue, vuetify, sync: false})
    expect(wrapper.find('.legal-logo').exists()).toBe(true)
  })
})
