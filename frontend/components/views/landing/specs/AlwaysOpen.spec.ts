import {createRouter, createWebHistory, Router} from 'vue-router'
import {cleanUp, flushPromises, mount, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {VueWrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty'
import searchSchema from '@/components/views/search/specs/fixtures'
import {FormController} from '@/store/forms/form-controller'
import AlwaysOpen from '@/components/views/landing/AlwaysOpen.vue'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let searchForm: FormController
let router: Router

describe('AlwaysOpen.vue', () => {
  beforeEach(async() => {
    store = createStore()
    searchForm = mount(Empty, vueSetup({store})).vm.$getForm('search', searchSchema())
    router = createRouter({
      history: createWebHistory(),
      routes: [{
        name: 'SearchProducts',
        path: '/search/products/',
        component: Empty,
      }, {
        name: 'BuyAndSell',
        path: '/faq/buy-and-sell/',
        component: Empty,
      }, {
        name: 'Home',
        path: '/',
        component: Empty,
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Calls Search', async() => {
    const wrapper = mount(AlwaysOpen, vueSetup({
      store,
      extraPlugins: [router],
    }))
    await router.isReady()
    await wrapper.find('.commission-cta').trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('SearchProducts')
    expect(router.currentRoute.value.query).toEqual({
      page: '1',
      size: '24',
    })
  })
})
