import {createRouter, createWebHistory, Router} from 'vue-router'
import {cleanUp, mount, vueSetup, waitFor} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import flushPromises from 'flush-promises'

let wrapper: VueWrapper<any>
let router: Router

describe('AcTabNav.vue', () => {
  beforeEach(async() => {
    router = createRouter({
      history: createWebHistory(),
      routes: [{
        path: '/characters/:username/',
        component: Empty,
        name: 'Characters',
      }, {
        path: '/gallery/:username/',
        component: Empty,
        name: 'Gallery',
      }, {
        path: '/profile/:username/',
        component: Empty,
        name: 'Profile',
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Renders tabs', async() => {
    await router.push('/profile/Fox/')
    await router.isReady()
    wrapper = mount(AcTabNav, {
      ...vueSetup({router}),
      props: {
        items: [{
          value: {
            name: 'Characters',
            params: {username: 'Fox'},
          },
          icon: 'mdi-people',
          title: 'Characters',
          count: 2,
        }, {
          value: {
            name: 'Gallery',
            params: {username: 'Fox'},
          },
          icon: 'mdi-image',
          title: 'Gallery',
        }],
        label: 'Stuff',
        headingLevel: 2,
      },
    })
    const tab = wrapper.find('.v-tab')
    expect(tab.attributes()['href']).toBe('/characters/Fox/')
  })
  // TODO: Fix this test. Can't get dropdown to appear.
  test('Navigates via dropdown', async() => {
    vi.useFakeTimers()
    await router.replace('/profile/Fox/')
    wrapper = mount(AcTabNav, {
      ...vueSetup({router}),
      props: {
        items: [{
          value: {name: 'Characters', params: {username: 'Fox'}}, icon: 'people', title: 'Characters', count: 2,
        }, {
          value: {name: 'Gallery', params: {username: 'Fox'}}, icon: 'image', title: 'Gallery',
        }],
        label: 'Stuff',
        headingLevel: 2,
      },
    })
    expect(router.currentRoute.value.name).toBe('Profile')
    // console.log(wrapper.find('.v-label').html())
    await wrapper.find('.v-label').trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()
    vi.runAllTimers()
    await wrapper.vm.$nextTick()
    const item = wrapper.find('.v-tab')
    expect(item.attributes()['href']).toBe('/characters/Fox/')
    await item.trigger('click')
    await waitFor(() => expect(router.currentRoute.value.name).toBe('Characters'))
  })
})
