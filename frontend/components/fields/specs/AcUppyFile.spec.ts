import AcUppyFile from '../AcUppyFile.vue'
import {Vuetify} from 'vuetify/types'
import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {cleanUp, createVuetify, docTarget, vueSetup} from '@/specs/helpers'
import flushPromises from 'flush-promises'
import {UppyFile} from '@uppy/core'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('ac-uppy-file.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts and initializes the uppy object', async() => {
    wrapper = mount(AcUppyFile, {
      localVue,
      vuetify,
      attachTo: docTarget(),

    })
    await flushPromises()
    expect((wrapper.vm as any).uppy).toBeTruthy()
  })
  it('Resets uppy when the reset button is clicked.', async() => {
    wrapper = mount(AcUppyFile, {
      localVue,
      vuetify,
      attachTo: docTarget(),

      propsData: {value: '123'},
    })
    await flushPromises()
    const spyEmit = jest.spyOn(wrapper.vm, '$emit')
    const spyReset = jest.spyOn((wrapper.vm as any).uppy, 'reset')
    wrapper.find('.uppy-reset-button').trigger('click')
    expect(spyEmit).toHaveBeenCalledWith('input', '')
    expect(spyReset).toHaveBeenCalled()
  })
  it('Resets uppy when the value is cleared.', async() => {
    wrapper = mount(AcUppyFile, {
      localVue,
      vuetify,
      attachTo: docTarget(),

      propsData: {value: '123'},
    })
    await flushPromises()
    const spyEmit = jest.spyOn(wrapper.vm, '$emit')
    const spyReset = jest.spyOn((wrapper.vm as any).uppy, 'reset')
    expect(spyEmit).not.toHaveBeenCalled()
    wrapper.setProps({value: ''})
    await wrapper.vm.$nextTick()
    expect(spyReset).toHaveBeenCalled()
  })
  it('Does not reset the value when uppy is populated.', async() => {
    wrapper = mount(AcUppyFile, {
      localVue,
      vuetify,
      attachTo: docTarget(),

      propsData: {value: ''},
    })
    await flushPromises()
    const spyEmit = jest.spyOn(wrapper.vm, '$emit')
    const spyReset = jest.spyOn((wrapper.vm as any).uppy, 'reset')
    expect(spyEmit).not.toHaveBeenCalled()
    wrapper.setProps({value: 'stuff'})
    await wrapper.vm.$nextTick()
    expect(spyReset).not.toHaveBeenCalled()
  })
  it('Clears the file when the clear button is clicked.', async() => {
    wrapper = mount(AcUppyFile, {
      localVue,
      vuetify,
      attachTo: docTarget(),

      propsData: {value: '123', showClear: true},
    })
    await flushPromises()
    const spyEmit = jest.spyOn(wrapper.vm, '$emit')
    wrapper.find('.uppy-clear-button').trigger('click')
    expect(spyEmit).toHaveBeenCalledWith('input', null)
  })
  it('Handles a successfully uploaded file.', async() => {
    wrapper = mount(AcUppyFile, {
      localVue,
      vuetify,
      attachTo: docTarget(),

    })
    await wrapper.vm.$nextTick()
    const spyEmit = jest.spyOn(wrapper.vm, '$emit')
    const file = {
      data: new Blob(),
      extension: 'jpg',
      isRemote: false,
      id: '1',
      meta: {name: 'test.jpg'},
      size: 100,
      name: 'test.jpg',
      progress: {
        uploadStarted: 1, uploadComplete: true, bytesTotal: 100, percentage: 100, bytesUploaded: 100,
      },
    };
    (wrapper.vm as any).uppy.state.files['1'] = file;
    (wrapper.vm as any).uppy.emit('upload-success', file, {body: {id: 'wat'}})
    expect(spyEmit).toHaveBeenCalledWith('input', 'wat')
  })
  it('Calls a callback on a successfully uploaded file.', async() => {
    const mockSuccess = jest.fn()
    wrapper = mount(AcUppyFile, {
      localVue,
      vuetify,
      attachTo: docTarget(),

      propsData: {success: mockSuccess},
    })
    await wrapper.vm.$nextTick() // Created
    // await wrapper.vm.$nextTick() // Mounted
    const file: UppyFile = {
      data: new Blob(),
      extension: 'jpg',
      isRemote: false,
      id: '1',
      meta: {name: 'test.jpg'},
      size: 100,
      name: 'test.jpg',
      progress: {
        uploadStarted: 1, uploadComplete: true, bytesTotal: 100, percentage: 100, bytesUploaded: 100,
      },
    };
    (wrapper.vm as any).uppy.state.files['1'] = file;
    (wrapper.vm as any).uppy.emit('upload-success', file, {body: {id: 'wat'}})
    expect(mockSuccess).toHaveBeenCalledWith({id: 'wat'})
  })
  it('Sets the proper label color when there are no errors.', async() => {
    const errorMessages: string[] = []
    wrapper = mount(AcUppyFile, {
      localVue,
      vuetify,
      attachTo: docTarget(),

      propsData: {errorMessages},
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.errorColor).toBe('primary')
  })
  it('Sets the proper label color when there are errors.', async() => {
    const errorMessages: string[] = ['Stuff']
    wrapper = mount(AcUppyFile, {
      localVue,
      vuetify,
      attachTo: docTarget(),

      propsData: {errorMessages},
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.errorColor).toBe('red')
  })
})
