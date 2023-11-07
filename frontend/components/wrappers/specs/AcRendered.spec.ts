import {cleanUp, mount, vueSetup} from '@/specs/helpers'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import AcRendered from '../AcRendered'
import {describe, expect, beforeEach, afterEach, test} from 'vitest'

describe('AcRendered.ts', () => {
  let wrapper: VueWrapper<any>
  let anchored: VueWrapper<any>
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
    if (anchored) {
      anchored.unmount()
    }
  })
  test('Truncates text at a specific length', () => {
    wrapper = mount(AcRendered, {
      ...vueSetup({
        store,
      }),
      props: {
        value: 'This is a section of text.',
        truncate: 10,
      },
    })
    expect(wrapper.text()).toBe('This is a...Read More')
  })
  test('Allows the user to read more', async() => {
    wrapper = mount(AcRendered, {
      ...vueSetup({
        store,
      }),
      props: {
        value: 'This is a section of text.',
        truncate: 10,
      },
    })
    await wrapper.find('.read-more-bar').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toBe('This is a section of text.')
  })
  test('Sets a default truncation level', async() => {
    wrapper = mount(AcRendered, {
      ...vueSetup({
        store,
      }),
      props: {
        value: ''.padStart(1500, 'A'),
        truncate: true,
      },
    })
    expect(wrapper.text()).toBe(''.padStart(1000, 'A') + '...Read More')
  })
  test('Shows default data', async() => {
    wrapper = mount(AcRendered, {
      ...vueSetup({
        store,
      }),
      props: {
        value: null,
        truncate: true,
      },
      slots: {
        empty: '<p>Nobody here but us chickens!</p>',
      },
    })
    expect(wrapper.text()).toBe('Nobody here but us chickens!')
  })
})
