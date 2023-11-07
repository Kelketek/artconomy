import {FormController} from '../form-controller'
import {formRegistry} from '../registry'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '../../index'
import Empty from '@/specs/helpers/dummy_components/empty'
import {RootFormState} from '@/store/forms/types/RootFormState'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {cleanUp, mount, vueSetup} from '@/specs/helpers'

describe('Form and field controllers', () => {
  let wrapper: VueWrapper<any>
  let store: ArtStore
  let state: RootFormState
  beforeEach(() => {
    formRegistry.resetValidators()
    store = createStore()
    state = (store.state as any).forms as RootFormState
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Registers a new form controller', () => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {name: {value: 'Fox'}, age: {value: 30}},
    })
    expect(formRegistry.controllers.example).toBe(controller)
  })
  test('Clears the form controller registry', () => {
    wrapper = mount(Empty, vueSetup({store}))
    formRegistry.controllers.example = new FormController({
      $store: store,
      $root: wrapper.vm.$root,
      initName: 'example',
      schema: {
        endpoint: '/endpoint/',
        fields: {
          name: {value: 'Fox'},
          age: {value: 30}
        },
      },
    })
    expect(formRegistry.controllers.example).toBeTruthy()
    formRegistry.reset()
    const result = {...formRegistry.controllers}
    delete result.__ob__
    expect(result).toEqual({})
  })
  test('Returns the cached form controller', () => {
    wrapper = mount(Empty, vueSetup({store}))
    const oldController = wrapper.vm.$getForm('example',
      {
        endpoint: '/endpoint/',
        fields: {name: {value: 'Fox'}, age: {value: 30}},
      },
    )
    const newController = wrapper.vm.$getForm('example',
      {
        endpoint: '/endpoint/',
        fields: {name: {value: 'Fox'}, age: {value: 30}},
      },
    )
    expect(newController).toBe(oldController)
  })
  test('Distinguishes between two different names', () => {
    wrapper = mount(Empty, vueSetup({store}))
    wrapper.vm.$getForm('example',
      {
        endpoint: '/endpoint/',
        fields: {name: {value: 'Fox'}, age: {value: 30}},
      },
    )
    const newController = wrapper.vm.$getForm('example2',
      {
        endpoint: '/endpoint/',
        fields: {stuff: {value: 'Thing'}},
      },
    )
    expect(newController.name.value).toBe('example2')
    expect(newController.fields.stuff).toBeTruthy()
  })
  test('Clears validators', () => {
    formRegistry.validators.test = () => []
    formRegistry.resetValidators()
    expect(formRegistry.validators).toEqual({})
  })
  test('Counts references to forms via UID', () => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {name: {value: 'Fox'}, age: {value: 30}},
    })
    const wrapper2 = mount(Empty, vueSetup({store}))
    const alsoController = wrapper2.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    expect(controller).toBe(alsoController)
    expect(formRegistry.uidTracking.example).toEqual([(wrapper.vm as any)._uid, (wrapper2.vm as any)._uid])
  })
  test('Adds references to controllers in the componentMap per component', () => {
    wrapper = mount(Empty, vueSetup({store}))
    const wrapper2 = mount(Empty, vueSetup({store}))
    const controller1 = wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    const controller2 = wrapper2.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    expect(controller1).toBe(controller2)
    expect(formRegistry.componentMap[(wrapper.vm as any)._uid]).toEqual([controller1])
    expect(formRegistry.componentMap[(wrapper2.vm as any)._uid]).toEqual([controller1])
  })
  test('Adds a component\'s UID to the uidTracking map', () => {
    wrapper = mount(Empty, vueSetup({store}))
    wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {name: {value: 'Fox'}, age: {value: 30}},
    })
    const wrapper2 = mount(Empty, vueSetup({store}))
    wrapper2.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    wrapper.unmount()
    expect(formRegistry.uidTracking.example).toEqual([(wrapper2.vm as any)._uid])
  })
  test('Adds references to the controller in the componentMap per component', () => {
    wrapper = mount(Empty, vueSetup({store}))
    wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    const uid = (wrapper.vm as any)._uid
    wrapper.unmount()
    expect(formRegistry.componentMap[uid]).toBe(undefined)
  })
  test('Deletes the form after the last reference is removed', () => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    const mockDelete = vi.spyOn(controller, 'purge')
    wrapper.unmount()
    expect(mockDelete).toHaveBeenCalled()
    expect(controller.purged).toBe(true)
  })
  test('Does not redelete the form if it has already been deleted', () => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    controller.purge()
    expect(controller.purged).toBe(true)
    const mockDelete = vi.spyOn(controller, 'purge')
    wrapper.unmount()
    expect(mockDelete).toHaveBeenCalledTimes(0)
  })
  test('Does not delete the form if it is marked persistent', () => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
      persistent: true,
    })
    const mockDelete = vi.spyOn(controller, 'purge')
    wrapper.unmount()
    expect(mockDelete).toHaveBeenCalledTimes(0)
  })
})
