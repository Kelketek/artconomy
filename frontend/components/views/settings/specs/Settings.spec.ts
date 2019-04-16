import Vue, {VueConstructor} from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Settings from '../Settings.vue'
import {ArtStore, createStore} from '@/store'
import Router from 'vue-router'
import {genUser} from '@/specs/helpers/fixtures'
import {setViewer, vuetifySetup} from '@/specs/helpers'
import Credentials from '../Credentials.vue'
import Avatar from '../Avatar.vue'
import Payment from '../payment/Payment.vue'
import Options from '../Options.vue'
import Purchase from '../payment/Purchase.vue'
import Artist from '../Artist.vue'
import {Singles} from '@/store/singles/registry'
import {Profiles} from '@/store/profiles/registry'
import Payout from '@/components/views/settings/payment/Payout.vue'
import TransactionHistory from '@/components/views/settings/payment/TransactionHistory.vue'
import {Lists} from '@/store/lists/registry'
import Premium from '@/components/views/settings/Premium.vue'

// Must use it directly, due to issues with package imports upstream.
Vue.use(Vuetify)
jest.useFakeTimers()

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
      name: 'Credentials',
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
  ],
}]

describe('Settings.vue', () => {
  let store: ArtStore
  let localVue: VueConstructor
  let wrapper: Wrapper<Vue>
  let router: Router
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(Singles)
    localVue.use(Lists)
    localVue.use(Profiles)
    store = createStore()
    vuetifySetup()
    if (wrapper) {
      wrapper.destroy()
    }
    localVue.use(Router)
    router = new Router({
      mode: 'history',
      routes: settingRoutes,
    })
  })
  it('Opens up a drawer when you click the settings button', async() => {
    setViewer(store, genUser())
    router.push({name: 'Settings', params: {username: 'Fox'}})
    wrapper = mount(Settings, {
      localVue,
      store,
      router,
      propsData: {username: 'Fox'},
      attachToDocument: true,
      sync: false,
    })
    expect((wrapper.vm as any).drawer).toBe(false)
    expect(wrapper.find('.v-navigation-drawer--open').exists()).toBe(false)
    wrapper.find('#more-settings-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.v-navigation-drawer--open').exists()).toBe(true)
  })
  it('Adds Options to the route if missing', async() => {
    setViewer(store, genUser())
    router.push({name: 'Settings', params: {username: 'Fox'}})
    wrapper = mount(Settings, {
      localVue,
      store,
      router,
      propsData: {username: 'Fox'},
      attachToDocument: true,
      sync: false,
    })
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.name).toBe('Options')
  })
  it('Loads the subordinate route', async() => {
    setViewer(store, genUser())
    router.push({name: 'Settings', params: {username: 'Fox'}})
    wrapper = mount(Settings, {
      localVue,
      store,
      router,
      propsData: {username: 'Fox'},
      attachToDocument: true,
      sync: false,
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#avatar-settings').exists()).toBe(false)
    router.push({name: 'Avatar', params: {username: 'Fox'}})
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#avatar-settings').exists()).toBe(true)
  })
})
