import {createRouter, createWebHistory, Router} from 'vue-router'
import {cleanUp, flushPromises, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import searchSchema from '@/components/views/search/specs/fixtures.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import ShieldCommissioner from '@/components/views/landing/ShieldCommissioner.vue'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let searchForm: FormController
let router: Router

describe('Shield.vue', () => {
  beforeEach(() => {
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
        path: '/faq/buy-and-sell/:question',
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
    const wrapper = mount(ShieldCommissioner, vueSetup({
      store,
      extraPlugins: [router],
    }))
    await wrapper.find('.commission-cta').trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('SearchProducts')
    expect(router.currentRoute.value.query).toEqual({
      shield_only: 'true',
      page: '1',
      size: '24',
    })
  })
})
