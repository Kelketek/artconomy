import {createRouter, Router} from 'vue-router'
import FAQ from '@/components/views/faq/FAQ.vue'
import {faqRoutes} from './helpers.ts'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, flushPromises, mount, vueSetup, waitFor} from '@/specs/helpers/index.ts'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

describe('FAQ.vue', () => {
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
    await router.push('/faq/')
    wrapper = mount(FAQ, vueSetup({
      store,
router,
    }))
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('About'))
  })
})
