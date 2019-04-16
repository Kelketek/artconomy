import Vue from 'vue'
import Router from 'vue-router'
import {vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import {VueRouter} from 'vue-router/types/router'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const localVue = vueSetup()
localVue.use(Router)
let wrapper: Wrapper<Vue>
let router: VueRouter

describe('AcTabNav.vue', () => {
  beforeEach(() => {
    router = new Router({
      mode: 'history',
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
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Renders tabs', async() => {
    router.replace('/profile/Fox/')
    wrapper = mount(AcTabNav, {router,
      localVue,
      propsData: {items: [{
        value: {name: 'Characters', params: {username: 'Fox'}}, icon: 'people', text: 'Characters', count: 2,
      }, {
        value: {name: 'Gallery', params: {username: 'Fox'}}, icon: 'image', text: 'Gallery',
      }]},
      sync: false,
      attachToDocument: true,
    })
    expect(wrapper.find('.v-tabs__item').text().replace(/\s\s+/g, ' ')).toBe(
      'people Characters (2)'
    )
  })
  it('Navigates via tab', async() => {
    router.replace('/profile/Fox/')
    wrapper = mount(AcTabNav, {router,
      localVue,
      propsData: {items: [{
        value: {name: 'Characters', params: {username: 'Fox'}}, icon: 'people', text: 'Characters', count: 2,
      }, {
        value: {name: 'Gallery', params: {username: 'Fox'}}, icon: 'image', text: 'Gallery',
      }]},
      sync: false,
      attachToDocument: true,
    })
    expect(wrapper.vm.$route.name).toBe('Profile')
    wrapper.find('.v-tabs__item').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$route.name).toBe('Characters')
  })
  it('Navigates via dropdown', async() => {
    router.replace('/profile/Fox/')
    wrapper = mount(AcTabNav, {router,
      localVue,
      propsData: {items: [{
        value: {name: 'Characters', params: {username: 'Fox'}}, icon: 'people', text: 'Characters', count: 2,
      }, {
        value: {name: 'Gallery', params: {username: 'Fox'}}, icon: 'image', text: 'Gallery',
      }]},
      sync: false,
      attachToDocument: true,
    })
    expect(wrapper.vm.$route.name).toBe('Profile')
    wrapper.find('.v-select__selections').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('.v-list__tile__title').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$route.name).toBe('Characters')
  })
})
