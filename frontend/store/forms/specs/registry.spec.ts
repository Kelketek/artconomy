import {FormController} from '../form-controller'
import {FormControllers, formRegistry} from '../registry'
import {createLocalVue, shallowMount} from '@vue/test-utils'
import Vue from 'vue'
import Vuex from 'vuex'
import {ArtStore, createStore} from '../../index'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import mockAxios from '@/specs/helpers/mock-axios'
import {RootFormState} from '@/store/forms/types/RootFormState'

Vue.use(Vuex)
const localVue = createLocalVue()
localVue.use(FormControllers)

describe('Form and field controllers', () => {
  let store: ArtStore
  let state: RootFormState
  beforeEach(() => {
    formRegistry.reset()
    formRegistry.resetValidators()
    mockAxios.reset()
    store = createStore()
    state = (store.state as any).forms as RootFormState
  })
  it('Registers a new form controller', () => {
    const wrapper = shallowMount(Empty, {store, localVue})
    const controller = wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {name: {value: 'Fox'}, age: {value: 30}},
    })
    expect(formRegistry.controllers.example).toBe(controller)
  })
  it('Clears the form controller registry', () => {
    formRegistry.controllers.example = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    }
    )
    expect(formRegistry.controllers.example).toBeTruthy()
    formRegistry.reset()
    const result = {...formRegistry.controllers}
    delete result.__ob__
    expect(result).toEqual({})
  })
  it('Returns the cached form controller', () => {
    const wrapper = shallowMount(Empty, {store, localVue})
    const oldController = wrapper.vm.$getForm('example',
      {
        endpoint: '/endpoint/',
        fields: {name: {value: 'Fox'}, age: {value: 30}},
      }
    )
    const newController = wrapper.vm.$getForm('example',
      {
        endpoint: '/endpoint/',
        fields: {name: {value: 'Fox'}, age: {value: 30}},
      }
    )
    expect(newController).toBe(oldController)
  })
  it('Distinguishes between two different names', () => {
    const wrapper = shallowMount(Empty, {store, localVue})
    wrapper.vm.$getForm('example',
      {
        endpoint: '/endpoint/',
        fields: {name: {value: 'Fox'}, age: {value: 30}},
      }
    )
    const newController = wrapper.vm.$getForm('example2',
      {
        endpoint: '/endpoint/',
        fields: {stuff: {value: 'Thing'}},
      }
    )
    expect(newController.name).toBe('example2')
    expect(newController.fields.stuff).toBeTruthy()
  })
  it('Clears validators', () => {
    formRegistry.validators.test = () => []
    formRegistry.resetValidators()
    expect(formRegistry.validators).toEqual({})
  })
  it('Counts references to forms via UID', () => {
    const wrapper1 = shallowMount(Empty, {store, localVue})
    const controller = wrapper1.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {name: {value: 'Fox'}, age: {value: 30}},
    })
    const wrapper2 = shallowMount(Empty, {store, localVue})
    const alsoController = wrapper2.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    expect(controller).toBe(alsoController)
    expect(formRegistry.uidTracking.example).toEqual([(wrapper1.vm as any)._uid, (wrapper2.vm as any)._uid])
  })
  it('Adds references to controllers in the componentMap per component', () => {
    const wrapper = shallowMount(Empty, {store, localVue})
    const wrapper2 = shallowMount(Empty, {store, localVue})
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
  it('Adds a component\'s UID to the uidTracking map', () => {
    const wrapper1 = shallowMount(Empty, {store, localVue})
    wrapper1.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {name: {value: 'Fox'}, age: {value: 30}},
    })
    const wrapper2 = shallowMount(Empty, {store, localVue})
    wrapper2.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    wrapper1.destroy()
    expect(formRegistry.uidTracking.example).toEqual([(wrapper2.vm as any)._uid])
  })
  it('Adds references to the controller in the componentMap per component', () => {
    const wrapper = shallowMount(Empty, {store, localVue})
    wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    const uid = (wrapper.vm as any)._uid
    wrapper.destroy()
    expect(formRegistry.componentMap[uid]).toBe(undefined)
  })
  it('Deletes the form after the last reference is removed', () => {
    const wrapper = shallowMount(Empty, {store, localVue})
    const controller = wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    const mockDelete = jest.spyOn(controller, 'purge')
    wrapper.destroy()
    expect(mockDelete).toHaveBeenCalled()
    expect(controller.purged).toBe(true)
  })
  it('Does not redelete the form if it has already been deleted', () => {
    const wrapper = shallowMount(Empty, {store, localVue})
    const controller = wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
    })
    controller.purge()
    expect(controller.purged).toBe(true)
    const mockDelete = jest.spyOn(controller, 'purge')
    wrapper.destroy()
    expect(mockDelete).toHaveBeenCalledTimes(0)
  })
  it('Does not delete the form if it is marked persistent', () => {
    const wrapper = shallowMount(Empty, {store, localVue})
    const controller = wrapper.vm.$getForm('example', {
      endpoint: '/endpoint/',
      fields: {},
      persistent: true,
    })
    const mockDelete = jest.spyOn(controller, 'purge')
    wrapper.destroy()
    expect(mockDelete).toHaveBeenCalledTimes(0)
  })
})
