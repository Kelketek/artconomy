import {createRouter, createWebHistory, Router} from 'vue-router'
import {cleanUp, mount, vueSetup} from '@/specs/helpers'
import {VueWrapper} from '@vue/test-utils'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import Empty from '@/specs/helpers/dummy_components/empty'
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
    router.push('/profile/Fox/')
    await router.isReady()
    wrapper = mount(AcTabNav, {
      ...vueSetup({extraPlugins: [router]}),
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
      },
    })
    const tab = wrapper.find('.v-tab')
    expect(tab.attributes()['href']).toBe('/characters/Fox/')
  })
  // TODO: Fix this test. Can't get dropdown to appear.
  // test('Navigates via dropdown', async() => {
  //   vi.useFakeTimers()
  //   await router.replace('/profile/Fox/')
  //   wrapper = mount(AcTabNav, {
  //     ...vueSetup({extraPlugins: [router]}),
  //     props: {
  //       items: [{
  //         value: {name: 'Characters', params: {username: 'Fox'}}, icon: 'people', title: 'Characters', count: 2,
  //       }, {
  //         value: {name: 'Gallery', params: {username: 'Fox'}}, icon: 'image', title: 'Gallery',
  //       }],
  //       label: 'Stuff',
  //     },
  //   })
  //   expect(wrapper.vm.$route.name).toBe('Profile')
  //   // console.log(wrapper.find('.v-label').html())
  //   await wrapper.find('.v-label').trigger('click')
  //   await wrapper.vm.$nextTick()
  //   await flushPromises()
  //   vi.runAllTimers()
  //   await wrapper.vm.$nextTick()
  //   const item = wrapper.find('.v-list-item__title')
  //   console.log(wrapper.html())
  //   expect(item.attributes()['href']).toBe('/characters/Fox/')
  //   expect(wrapper.vm.$route.name).toBe('Characters')
  // })
})
