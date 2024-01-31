import AcUppyFile from '../AcUppyFile.vue'
import {VueWrapper} from '@vue/test-utils'
import {cleanUp, mount, vueSetup} from '@/specs/helpers'
import flushPromises from 'flush-promises'
import {ArtStore, createStore} from '@/store'
import {UppyFile} from '@uppy/core'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let wrapper: VueWrapper<any>
let store: ArtStore

describe('ac-uppy-file.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  const makeUppy = (props?: any) => {
    return mount(AcUppyFile, {
      ...vueSetup({store}),
      props: {uppyId: 'uppyTest', ...props},
    })
  }
  test('Mounts and initializes the uppy object', async() => {
    wrapper = makeUppy()
    await flushPromises()
    expect((wrapper.vm as any).uppy).toBeTruthy()
  })
  test('Resets uppy when the reset button is clicked.', async() => {
    wrapper = makeUppy({modelValue: '123'})
    await flushPromises()
    const spyEmit = vi.spyOn(wrapper.vm, '$emit')
    const spyReset = vi.spyOn((wrapper.vm as any).uppy, 'cancelAll')
    await wrapper.find('.uppy-reset-button').trigger('click')
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([''])
    expect(spyReset).toHaveBeenCalled()
  })
  test('Resets uppy when the modelValue is cleared.', async() => {
    wrapper = makeUppy({modelValue: '123'})
    await flushPromises()
    const spyReset = vi.spyOn((wrapper.vm as any).uppy, 'cancelAll')
    expect(wrapper.emitted('update:modelValue')).toBe(undefined)
    await wrapper.setProps({modelValue: ''})
    await wrapper.vm.$nextTick()
    expect(spyReset).toHaveBeenCalled()
  })
  test('Does not reset the modelValue when uppy is populated.', async() => {
    wrapper = makeUppy({modelValue: ''})
    await flushPromises()
    const spyReset = vi.spyOn((wrapper.vm as any).uppy, 'cancelAll')
    expect(wrapper.emitted('update:modelValue')).toBe(undefined)
    await wrapper.setProps({modelValue: 'stuff'})
    await wrapper.vm.$nextTick()
    expect(spyReset).not.toHaveBeenCalled()
  })
  test('Clears the file when the clear button is clicked.', async() => {
    wrapper = makeUppy({
      modelValue: '123',
      showClear: true,
    })
    await flushPromises()
    await wrapper.find('.uppy-clear-button').trigger('click')
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([null])
  })
  test('Handles a successfully uploaded file.', async() => {
    wrapper = makeUppy()
    await wrapper.vm.$nextTick()
    const file = {
      data: new Blob(),
      extension: 'jpg',
      isRemote: false,
      id: '1',
      meta: {name: 'test.jpg'},
      size: 100,
      name: 'test.jpg',
      providerName: 'URL',
      remote: {
        host: 'example.com',
        url: 'https://example.com/example.jpg',
      },
      progress: {
        uploadStarted: 1,
        uploadComplete: true,
        bytesTotal: 100,
        percentage: 100,
        bytesUploaded: 100,
      },
    };
    (wrapper.vm as any).uppy.setState({files: {1: file}});
    (wrapper.vm as any).uppy.emit('upload-success', file, {body: {id: 'wat'}})
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['wat'])
  })
  test('Handles multiple files.', async() => {
    wrapper = makeUppy({
      maxNumberOfFiles: 3,
      modelValue: ['wat'],
    })
    await wrapper.vm.$nextTick()
    const file: UppyFile = {
      data: new Blob(),
      extension: 'jpg',
      isRemote: false,
      id: '1',
      meta: {name: 'test2.jpg'},
      size: 100,
      name: 'test2.jpg',
      remote: {
        host: 'example.com',
        url: 'https://example.com/example.jpg',
      },
      progress: {
        uploadStarted: 1,
        uploadComplete: true,
        bytesTotal: 100,
        percentage: 100,
        bytesUploaded: 100,
      },
    }
    const vm = wrapper.vm as any
    vm.uppy.setState({files: {1: file}})
    vm.uppy.emit('upload-success', file, {body: {id: 'do'}})
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([['wat', 'do']])
  })
  test('Sets the proper label color when there are no errors.', async() => {
    const errorMessages: string[] = []
    wrapper = makeUppy({errorMessages})
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.errorColor).toBe('primary')
  })
  test('Sets the proper label color when there are errors.', async() => {
    const errorMessages: string[] = ['Stuff']
    wrapper = makeUppy({
      errorMessages,
      uppyId: 'uppyTest',
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.errorColor).toBe('red')
  })
})
