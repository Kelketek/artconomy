import {VueWrapper} from '@vue/test-utils'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import Editor from '@/specs/helpers/dummy_components/editor.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import AcEditor from '@/components/fields/AcEditor.vue'

let store: ArtStore
let wrapper: VueWrapper<any>

const mockError = vi.spyOn(console, 'error')

describe('ac-editor', () => {
  beforeEach(() => {
    store = createStore()
    mockError.mockImplementationOnce(() => undefined)
  })
  afterEach(() => {
    mockError.mockClear()
    cleanUp(wrapper)
  })
  test('Mounts the editor', async() => {
    wrapper = mount(Editor, vueSetup({store}))
  })
  test('Auto saves changes', async() => {
    wrapper = mount(AcEditor, {
      ...vueSetup({store}),
      props: {
        autoSave: true,
        modelValue: '',
      },
    })
    wrapper.vm.scratch = 'Hello there!'
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['Hello there!'])
  })
  test('Saves changes manually', async() => {
    wrapper = mount(Editor, vueSetup({store}))
    await wrapper.find('#editor-manual textarea').setValue('Hello there!')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).things).toBe('')
  })
  test('Does not propagate the changes down when manually controlled', async() => {
    wrapper = mount(Editor, vueSetup({store}))
    const mockEmit = vi.spyOn(wrapper.vm.$refs.auto as any, '$emit');
    (wrapper.vm as any).things = 'Hello there!'
    await wrapper.vm.$nextTick()
    expect((wrapper.vm.$refs.manual as any).scratch).toBe('')
    expect(mockEmit).not.toHaveBeenCalled()
  })
  test('Previews the result', async() => {
    wrapper = mount(AcEditor, {
      ...vueSetup({store}),
      props: {modelValue: '# Hello there!'},
    })
    await wrapper.find('.preview-mode-toggle').trigger('click')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).previewMode).toBe(true)
    expect(wrapper.find('.editor-preview h1').text()).toBe('Hello there!')
  })
})
