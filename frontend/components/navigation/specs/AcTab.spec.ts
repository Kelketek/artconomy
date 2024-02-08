import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import AcTabs from '@/components/navigation/AcTabs.vue'
import {describe, expect, afterEach, test} from 'vitest'

let wrapper: VueWrapper<any>

describe('AcTabNav.vue', () => {
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Renders tabs', async() => {
    wrapper = mount(AcTabs, {
      ...vueSetup(),
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
        modelValue: 0,
        label: 'Stuff',
      },
    })
    expect(wrapper.find('.v-tab').text().replace(/\s\s+/g, ' ')).toEqual(
      'Characters (2)',
    )
  })
  test('Navigates via dropdown', async() => {
    wrapper = mount(AcTabs, {
      ...vueSetup(),
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
        modelValue: 0,
        label: 'Stuff',
      },
    })
    expect(wrapper.find('.v-select__selections').exists())
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.v-tab').text().replace(/\s\s+/g, ' ')).toEqual(
      'Characters (2)',
    )
  })
})
