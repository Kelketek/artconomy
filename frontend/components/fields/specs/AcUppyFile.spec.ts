import AcUppyFile from '../AcUppyFile.vue'
import {VueWrapper} from '@vue/test-utils'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import flushPromises from 'flush-promises'
import {ArtStore, createStore} from '@/store/index.ts'
import {Body, Meta, UppyFile} from '@uppy/core'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {nextTick} from 'vue'

let wrapper: VueWrapper<any>
let store: ArtStore

describe('AcUppyFile.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  const makeUppy = (props: any) => {
    return mount(AcUppyFile, {
      ...vueSetup({store}),
      props: {uppyId: 'uppyTest', ...props},
    })
  }
  test('Mounts and initializes the uppy object', async() => {
    wrapper = makeUppy({modelValue: '', label: 'Boop'})
    await flushPromises()
    expect((wrapper.vm as any).uppy).toBeTruthy()
  })
  test('Resets uppy when the reset button is clicked.', async() => {
    wrapper = makeUppy({modelValue: '123', label: 'Boop'})
    await flushPromises()
    vi.spyOn(wrapper.vm, '$emit')
    const spyReset = vi.spyOn((wrapper.vm as any).uppy, 'cancelAll')
    await wrapper.find('.uppy-reset-button').trigger('click')
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([''])
    expect(spyReset).toHaveBeenCalled()
  })
  test('Resets uppy when the modelValue is cleared.', async() => {
    wrapper = makeUppy({modelValue: '123', label: 'Beep'})
    await flushPromises()
    const spyReset = vi.spyOn((wrapper.vm as any).uppy, 'cancelAll')
    expect(wrapper.emitted('update:modelValue')).toBe(undefined)
    await wrapper.setProps({modelValue: ''})
    await wrapper.vm.$nextTick()
    expect(spyReset).toHaveBeenCalled()
  })
  test('Does not reset the modelValue when uppy is populated.', async() => {
    wrapper = makeUppy({modelValue: '', label: 'Beep'})
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
      label: 'Beep',
      showClear: true,
    })
    await flushPromises()
    await wrapper.find('.uppy-clear-button').trigger('click')
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([null])
  })
  test('Handles a successfully uploaded file.', async() => {
    wrapper = makeUppy({modelValue: '', label: 'Boop'})
    await wrapper.vm.$nextTick()
    const file: UppyFile<Meta, Body> = {
      data: new Blob(),
      extension: 'jpg',
      isRemote: false,
      id: '1',
      meta: {name: 'test.jpg'},
      size: 100,
      name: 'test.jpg',
      isGhost: false,
      type: 'URL',
      remote: {
        host: 'example.com',
        requestClientId: 'blabla',
        companionUrl: 'https://example.com/companion/',
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
    wrapper.vm.uppy.setState({files: {1: file}})
    wrapper.vm.uppy.emit('upload-success', file, {body: {id: 'wat'}})
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['wat'])
  })
  test('Handles multiple files.', async() => {
    wrapper = makeUppy({
      maxNumberOfFiles: 3,
      modelValue: ['wat'],
      label: 'Beep',
    })
    await wrapper.vm.$nextTick()
    const file: UppyFile<Meta, Body> = {
      data: new Blob(),
      extension: 'jpg',
      isRemote: false,
      id: '1',
      meta: {name: 'test2.jpg'},
      size: 100,
      name: 'test2.jpg',
      isGhost: false,
      type: 'XHR',
      remote: {
        host: 'example.com',
        requestClientId: 'blabla',
        companionUrl: 'https://example.com/companion/',
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
    const vm = wrapper.vm
    vm.uppy.setState({files: {1: file}})
    vm.uppy.emit('upload-success', file, {body: {id: 'do'}})
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([['wat', 'do']])
  })
  test('Sets the proper label color when there are no errors.', async() => {
    const errorMessages: string[] = []
    wrapper = makeUppy({errorMessages, modelValue: '', label: 'Beep'})
    await nextTick()
    const vm = wrapper.vm
    expect(vm.errorColor).toBe('primary')
  })
  test('Sets the proper label color when there are errors.', async() => {
    const errorMessages: string[] = ['Stuff']
    wrapper = makeUppy({
      label: 'Beep',
      modelValue: '',
      errorMessages,
      uppyId: 'uppyTest',
    })
    await nextTick()
    const vm = wrapper.vm as any
    expect(vm.errorColor).toBe('red')
  })
})
