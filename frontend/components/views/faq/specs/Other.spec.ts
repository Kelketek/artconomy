import {createRouter, Router} from 'vue-router'
import {faqRoutes} from './helpers'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import Other from '@/components/views/faq/Other.vue'
import {cleanUp, flushPromises, mount, vueSetup} from '@/specs/helpers'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

describe('Other.vue', () => {
  let router: Router
  let wrapper: VueWrapper<any>
  let store: ArtStore
  beforeEach(() => {
    router = createRouter(faqRoutes())
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('mounts', async() => {
    await router.push('/faq/other/')
    wrapper = mount(Other, vueSetup({
      store,
      extraPlugins: [router],
    }))
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.value.params).toEqual({question: 'content-ratings'})
  })
})
