import {VueWrapper} from '@vue/test-utils'
import Settings from '../Settings.vue'
import {ArtStore, createStore} from '@/store/index.ts'
import {Router, createRouter, createWebHistory} from 'vue-router'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {cleanUp, createTestRouter, flushPromises, mount, vueSetup, VuetifyWrapped} from '@/specs/helpers/index.ts'
import Credentials from '../Credentials.vue'
import Avatar from '../Avatar.vue'
import Payment from '../payment/Payment.vue'
import Options from '../Options.vue'
import Purchase from '../payment/Purchase.vue'
import Artist from '../Artist.vue'
import Payout from '@/components/views/settings/payment/Payout.vue'
import TransactionHistory from '@/components/views/settings/payment/TransactionHistory.vue'
import Premium from '@/components/views/settings/Premium.vue'
import Invoices from '../payment/Invoices.vue'
import Email from '@/components/views/settings/Email.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

vi.useFakeTimers()

const settingRoutes = [{
  path: '/profile/:username/settings/',
  name: 'Settings',
  component: Settings,
  props: true,
  meta: {
    sideNav: true,
  },
  children: [
    {
      name: 'Login Details',
      path: 'credentials',
      component: Credentials,
      props: true,
    },
    {
      name: 'Avatar',
      path: 'avatar',
      component: Avatar,
      props: true,
    },
    {
      name: 'Payment',
      path: 'payment',
      component: Payment,
      props: true,
      children: [
        {
          name: 'Purchase',
          path: 'purchase',
          component: Purchase,
          props: true,
        },
        {
          name: 'Payout',
          path: 'payout',
          component: Payout,
          props: true,
        },
        {
          name: 'Invoices',
          path: 'invoices',
          component: Invoices,
          props: true,
        },
        {
          name: 'TransactionHistory',
          path: 'transactions',
          component: TransactionHistory,
          props: true,
        },
      ],
    },
    {
      name: 'Artist',
      path: 'artist',
      component: Artist,
      props: true,
    }, {
      name: 'Premium',
      path: 'premium',
      component: Premium,
      props: true,
    }, {
      name: 'Options',
      path: 'options',
      component: Options,
      props: true,
    },
    {
      name: 'Email',
      path: 'email',
      component: Email,
      props: true,
    },
  ],
}]

const WrappedSettings = VuetifyWrapped(Settings)

describe('Settings.vue', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  let router: Router
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: settingRoutes,
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Opens up a drawer when you click the settings button', async() => {
    setViewer(store, genUser())
    await router.push({
      name: 'Settings',
      params: {username: 'Fox'},
    })
    wrapper = mount(WrappedSettings, {
      ...vueSetup({
        store,
        router,
      }),
      props: {username: 'Fox'},
    })
    expect((wrapper.vm.$refs.vm as any).drawer).toBe(false)
    // Upstream Type is missing an annotation here.
    // @ts-ignore
    expect(wrapper.find('.v-navigation-drawer').element.style.getPropertyValue('transform')).toEqual('translateX(-110%)')
    await wrapper.find('#more-settings-button').trigger('click')
    await wrapper.vm.$nextTick()
    // @ts-ignore
    expect(wrapper.find('.v-navigation-drawer').element.style.getPropertyValue('transform')).toEqual('translateX(0%)')
  })
  test('Adds Options to the route if missing', async() => {
    setViewer(store, genUser())
    await router.push({
      name: 'Settings',
      params: {username: 'Fox'},
    })
    wrapper = mount(WrappedSettings, {
      ...vueSetup({
        store,
        router,
      }),
      props: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('Options')
  })
  test('Loads the subordinate route', async() => {
    setViewer(store, genUser())
    await router.push({
      name: 'Settings',
      params: {username: 'Fox'},
    })
    wrapper = mount(WrappedSettings, {
      ...vueSetup({
        store,
        router,
      }),
      props: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#avatar-settings').exists()).toBe(false)
    await router.push({
      name: 'Avatar',
      params: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#avatar-settings').exists()).toBe(true)
  })
})
