import {createRouter, Router} from 'vue-router'
import {faqRoutes} from './helpers.ts'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import BuyAndSell from '@/components/views/faq/BuyAndSell.vue'
import {
  cleanUp,
  createTestRouter,
  flushPromises,
  mount,
  setPricing,
  VueMountOptions,
  vueSetup, waitFor,
} from '@/specs/helpers/index.ts'
import searchSchema from '@/components/views/search/specs/fixtures.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'
import {nextTick} from 'vue'
import type {StripeCountryList} from '@/types/main'

let searchForm: FormController
let countryList: SingleController<StripeCountryList>

describe('BuyAndSell.vue', () => {
  let router: Router
  let wrapper: VueWrapper<any>
  let store: ArtStore
  let options: VueMountOptions
  beforeEach(() => {
    router = createTestRouter()
    store = createStore()
    options = {
      props: {
        question: 'how-to-buy',
      },
      ...vueSetup({
        store,
        router,
      })
    }
    searchForm = mount(Empty, {
      ...options,
      attachTo: '',
    }).vm.$getForm('search', searchSchema())
    countryList = mount(Empty, {
      ...options,
      attachTo: '',
    }).vm.$getSingle('stripeCountries', {
      x: {
        countries: [{
          value: 'stuff',
          title: 'things',
        }],
      },
      endpoint: '/stuff/',
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Shows the buy and sell FAQ', async() => {
    await router.push('/faq/buying-and-selling/')
    wrapper = mount(BuyAndSell, options)
    const vm = wrapper.vm as any
    await nextTick()
    await flushPromises()
    expect(router.currentRoute.value.params).toEqual({question: 'how-to-buy'})
    setPricing(store)
    await vm.$nextTick()
  })
  test('Sends the user to search', async() => {
    searchForm.fields.q.update('stuff', false)
    await router.push('/faq/buying-and-selling/')
    wrapper = mount(BuyAndSell, options)
    await nextTick()
    await wrapper.find('.who-is-open-link').trigger('click')
    await waitFor(() => expect(router.currentRoute.value.name).toBe('SearchProducts'))
    expect(searchForm.fields.q.model).toBe('')
  })
})
