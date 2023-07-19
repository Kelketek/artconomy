import Vue from 'vue'
import {FormControllers, formRegistry} from '../registry'
import {axiosCatch, FieldController} from '../field-controller'
import {FormController} from '../form-controller'
import {ArtStore, createStore} from '../../index'
import {createLocalVue, shallowMount, Wrapper} from '@vue/test-utils'
import mockAxios from '@/specs/helpers/mock-axios'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'
import {CancelToken} from 'axios'
import ErrorScrollTests from '@/specs/helpers/dummy_components/scroll-tests.vue'
import {RootFormState} from '@/store/forms/types/RootFormState'
import {docTarget, mount} from '@/specs/helpers'

Vue.use(Vuex)
const localVue = createLocalVue()
localVue.use(FormControllers)

const mockScrollIntoView = Element.prototype.scrollIntoView = jest.fn()

function min(field: FieldController, minimum: number, message?: string): string[] {
  if (field.value < minimum) {
    return [message || 'Too low.']
  }
  return []
}

async function alwaysFail(field: FieldController, cancelToken: CancelToken, arg: string) {
  expect(arg).toEqual('test')
  return new Promise<string[]>((resolve) => resolve(['I failed!']))
}

// noinspection JSUnusedLocalSymbols
async function alwaysSucceed(field: FieldController, cancelToken: CancelToken) {
  return new Promise<string[]>((resolve) => resolve([]))
}

const mockError = jest.spyOn(console, 'error')
const mockTrace = jest.spyOn(console, 'trace')

describe('Form and field controllers', () => {
  let store: ArtStore
  let state: RootFormState
  let wrapper: Wrapper<Vue>
  beforeEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
    formRegistry.reset()
    formRegistry.resetValidators()
    mockAxios.reset()
    store = createStore()
    state = (store.state as any).forms as RootFormState
    mockError.mockClear()
    mockTrace.mockClear()
    mockScrollIntoView.mockClear()
  })
  it('Initializes a form controller', async() => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          errors: ['Borked.'],
          fields: {name: {value: 'Fox', errors: ['Too cool.']}, age: {value: 30}},
        },
      },
    },
    )
    expect(controller.name).toBe('example')
    expect(controller.purged).toBe(false)
    expect(controller.fields).toBeTruthy()
    expect(controller.fields.name).toBeTruthy()
    expect(controller.fields.name.fieldName).toBe('name')
    expect(controller.fields.name.formName).toBe('example')
    expect(controller.fields.age.fieldName).toBe('age')
    expect(controller.fields.age.formName).toBe('example')
    expect(controller.errors).toEqual(['Borked.'])
    expect(state.example.fields.name.initialData).toBe('Fox')
    expect(state.example.method).toBe('post')
    expect(state.example.fields.age.initialData).toBe(30)
  })
  it('Submits a form through a FormController', async() => {
    const success = jest.fn()
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    })
    controller.submitThen(success).then()
    mockAxios.mockResponse({status: 200, data: {test: 'result'}})
    await flushPromises()
    expect(success).toBeCalled()
    expect(success).toBeCalledWith({test: 'result'})
  })
  it('Allows manual toggle of sending status', async() => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    })
    controller.sending = true
    expect(state.example.sending).toBe(true)
    controller.sending = false
    expect(state.example.sending).toBe(false)
  })
  it('Clears errors', async() => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          errors: ['Too amazing'],
          fields: {name: {value: 'Fox', errors: ['Too cool.']}, age: {value: 30}},
        },
      },
    })
    expect(state.example.errors).toEqual(['Too amazing'])
    expect(state.example.fields.name.errors).toEqual(['Too cool.'])
    controller.clearErrors()
    expect(state.example.errors).toEqual([])
    expect(state.example.fields.name.errors).toEqual([])
  })
  it('Recognizes failed steps', async() => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          errors: ['Too amazing'],
          fields: {
            name: {value: 'Fox', errors: ['Too cool.']},
            age: {value: 30, errors: ['Wat'], step: 2},
            things: {value: '', step: 3},
          },
        },
      },
    })
    expect(state.example.errors).toEqual(['Too amazing'])
    expect(state.example.fields.name.errors).toEqual(['Too cool.'])
    expect(controller.failedSteps).toEqual([1, 2])
  })
  it('Sets field-specific errors upon a failed request', async() => {
    const success = jest.fn()
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 20}},
        },
      },
    },
    )
    controller.submitThen(success).then()
    store.dispatch('forms/submit', {name: 'example'}).then()
    mockAxios.mockError!({response: {data: {age: ['You stopped being 20 a long time ago.']}}})
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual(['You stopped being 20 a long time ago.'])
    expect(controller.fields.name.errors).toEqual([])
  })
  it('Sets the right step upon a failed request', async() => {
    const success = jest.fn()
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 20, step: 2}, stuff: {value: 2, step: 3}},
        },
      },
    },
    )
    controller.step = 3
    expect(controller.step).toBe(3)
    controller.submitThen(success).then()
    store.dispatch('forms/submit', {name: 'example'}).then()
    mockAxios.mockError!({response: {data: {age: ['You stopped being 20 a long time ago.']}}})
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.step).toBe(2)
  })
  it('Sets a general error upon a failed request', async() => {
    const success = jest.fn()
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 20}},
        },
      },
    },
    )
    controller.submitThen(success).then()
    store.dispatch('forms/submit', {name: 'example'}).then()
    mockTrace.mockImplementationOnce(() => undefined)
    mockAxios.mockError!({})
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual([])
    expect(controller.errors).toEqual(['We had an issue contacting the server. Please try again later!'])
    expect(mockTrace).toHaveBeenCalled()
  })
  it('Sets a general error upon a DRF error message', async() => {
    const success = jest.fn()
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 20}},
        },
      },
    },
    )
    controller.submitThen(success).then()
    store.dispatch('forms/submit', {name: 'example'}).then()
    mockAxios.mockError!({response: {data: {detail: 'This is a thing.'}}})
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual([])
    expect(controller.errors).toEqual(['This is a thing.'])
  })
  it('Sets a general errors upon array error messages', async() => {
    const success = jest.fn()
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 20}},
        },
      },
    },
    )
    controller.submitThen(success).then()
    store.dispatch('forms/submit', {name: 'example'}).then()
    mockAxios.mockError!({response: {data: ['This is a thing.']}})
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual([])
    expect(controller.errors).toEqual(['This is a thing.'])
  })
  it('Sets general errors upon a non-json error response', async() => {
    const success = jest.fn()
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 20}},
        },
      },
    },
    )
    controller.submitThen(success).then()
    store.dispatch('forms/submit', {name: 'example'}).then()
    mockTrace.mockImplementationOnce(() => undefined)
    mockAxios.mockError!({response: {data: 'Stuff'}})
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual([])
    expect(controller.errors).toEqual(['We had an issue contacting the server. Please try again later!'])
    expect(mockTrace).toHaveBeenCalled()
  })
  it('Lets us know if we forgot a field', async() => {
    const success = jest.fn()
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 20}},
        },
      },
    },
    )
    controller.submitThen(success).then()
    store.dispatch('forms/submit', {name: 'example'}).then()
    mockAxios.mockError!({response: {data: {other_field: ['You forgot me.']}}})
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual([])
    expect(controller.errors).toEqual(
      [
        'Whoops! We had a coding error. Please contact support and tell them the following: ' +
        'other_field: You forgot me.',
      ],
    )
  })
  it('Adds a field to the FormController when the schema is updated', () => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    },
    )
    store.commit(
      'forms/addField', {name: 'example', field: {name: 'sex', schema: {value: 'Male'}}},
    )
    expect(controller.fields.sex).toBeTruthy()
    expect(controller.fields.sex.fieldName).toBe('sex')
    expect(controller.fields.sex.formName).toBe('example')
  })
  it('Does not add a field to the FormController when a different form is updated', () => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
          errors: ['Borked.'],
        },
      },
    },
    )
    // eslint-disable-next-line no-new
    new FormController({
      store,
      propsData: {
        initName: 'example2',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
          errors: ['Borked.'],
        },
      },
    },
    )
    store.commit(
      'forms/addField', {name: 'example2', field: {name: 'sex', schema: {value: 'Male'}}},
    )
    expect(controller.fields.sex).toBe(undefined)
  })
  it('Removes a field from the FormController when the schema is updated', () => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    },
    )
    store.commit(
      'forms/delField', {name: 'example', field: 'age'},
    )
    expect(controller.fields.age).toBe(undefined)
  })
  it('Does not remove a field from the FormController when deleting from a different form.', () => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox', errors: ['Too cool.']}, age: {value: 30}},
        },
      },
    },
    )
    // eslint-disable-next-line no-new
    new FormController({
      store,
      propsData: {
        initName: 'example2',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox', errors: ['Too cool.']}, age: {value: 30}},
        },
      },
    },
    )
    store.commit(
      'forms/delField', {name: 'example2', field: 'age'},
    )
    expect(controller.fields.age).toBeTruthy()
  })
  it('Handles deletion of the form in a FormController', () => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    },
    )
    store.commit(
      'forms/delForm', {name: 'example'},
    )
    expect(Object.keys(controller.fields)).toEqual([])
    expect(controller.purged).toBe(true)
    expect(controller.errors).toEqual([])
  })
  it('Doesn\'t self-delete if deleting a different form', () => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    },
    )
    store.commit(
      'forms/delForm', {name: 'example2'},
    )
    expect(Object.keys(controller.fields)).toBeTruthy()
    expect(controller.purged).toBe(false)
  })
  it('Updates the endpoint of the form', async() => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {},
        },
      },
    },
    )
    expect(state.example.endpoint).toBe('/endpoint/')
    controller.endpoint = '/wat/'
    expect(state.example.endpoint).toBe('/wat/')
  })
  it('Retrieves an attribute of a form', async() => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {},
        },
      },
    },
    )
    expect(controller.attr('endpoint')).toBe('/endpoint/')
  })
  it('Retrieves calculated data from a form', async() => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {stuff: {value: 'things'}, wat: {value: 'do', omitIf: 'do'}, goober: {value: 100}},
        },
      },
    },
    )
    expect(controller.rawData).toEqual({stuff: 'things', goober: 100})
  })
  it('Allows deletion of the form through a FormController', () => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    })
    expect(state.example).toBeTruthy()
    expect(formRegistry.controllers).toBeTruthy()
    controller.purge()
    expect(state.example).toBe(undefined)
    const result = {...formRegistry.controllers}
    delete result.__ob__
    expect(result).toEqual({})
    expect(Object.keys(controller.fields)).toEqual([])
    expect(controller.purged).toBe(true)
  })
  it('Scrolls to errors in scrollable text', async() => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    })
    wrapper = shallowMount(ErrorScrollTests, {
      localVue,
      propsData: {test: 'scrollableText'},
      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    const element = document.querySelector('#scrollable-text-error') as Element
    controller.scrollToError()
    expect(element.scrollIntoView).toHaveBeenCalledWith({behavior: 'smooth', block: 'center'})
  })
  it('Scrolls to errors in ID only', async() => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    })
    wrapper = shallowMount(ErrorScrollTests, {
      localVue,
      propsData: {test: 'idOnly'},
      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    const element = document.querySelector('#id-only-error') as Element
    controller.scrollToError()
    expect(element.scrollIntoView).toHaveBeenCalledWith({behavior: 'smooth', block: 'center'})
  })
  it('Does not break if there are no errors in the form ID when attempting to scroll', async() => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    })
    wrapper = shallowMount(ErrorScrollTests, {
      localVue,
      propsData: {test: 'noError'},
      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    controller.scrollToError()
    expect(Element.prototype.scrollIntoView).not.toHaveBeenCalled()
  })
  it('Does not break if there is no form to scroll to', async() => {
    const controller = new FormController({
      store,
      propsData: {
        initName: 'example',
        schema: {
          endpoint: '/endpoint/',
          fields: {name: {value: 'Fox'}, age: {value: 30}},
        },
      },
    })
    wrapper = shallowMount(ErrorScrollTests, {
      localVue,
      propsData: {test: 'noErrorNoId'},
      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    controller.scrollToError()
    expect(Element.prototype.scrollIntoView).not.toHaveBeenCalled()
  })
  it('Initializes a field controller', () => {
    store.commit('forms/initForm', {
      name: 'example',
      fields: {name: {value: 'Fox', errors: ['Too cool.']}, age: {value: 30}},
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'name'}})
    expect(controller.fieldName).toBe('name')
    expect(controller.formName).toBe('example')
    expect(controller.value).toBe('Fox')
    expect(controller.errors).toEqual(['Too cool.'])
  })
  it('Updates a field', async() => {
    store.commit('forms/initForm', {
      name: 'example',
      fields: {name: {value: 'Fox', errors: ['Too cool.']}, age: {value: 30}},
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'name'}})
    expect(controller.fieldName).toBe('name')
    expect(controller.formName).toBe('example')
    expect(controller.value).toBe('Fox')
    expect(controller.errors).toEqual(['Too cool.'])
    controller.update('Amber')
    controller.validate.flush()
    await flushPromises()
    expect(state.example.fields.name.value).toBe('Amber')
    expect(controller.value).toBe('Amber')
    expect(controller.errors).toEqual([])
  })
  it('Produces field bindings', () => {
    store.commit('forms/initForm', {
      name: 'example',
      fields: {
        name: {value: 'Fox', errors: ['Too cool.'], extra: {checked: true}},
        age: {value: 30},
      },
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'name'}})
    expect(controller.bind).toEqual(
      {
        value: 'Fox',
        inputValue: 'Fox',
        errorMessages: ['Too cool.'],
        disabled: false,
        checked: true,
        id: 'field-example__name',
      },
    )
    expect(controller.on).toEqual({
      change: controller.update, input: controller.update, blur: controller.forceValidate,
    },
    )
  })
  it('Retrieves attributes', () => {
    store.commit('forms/initForm', {
      name: 'example',
      fields: {
        name: {value: 'Fox', errors: ['Too cool.'], disabled: true},
        age: {value: 30},
      },
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'name'}})
    expect(controller.attr('disabled')).toBe(true)
  })
  it('Uses the debounce rate of the form by default', () => {
    store.commit('forms/initForm', {
      name: 'example',
      fields: {
        name: {value: 'Fox', errors: ['Too cool.'], disabled: true},
        age: {value: 30},
      },
      debounce: 500,
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'name'}})
    expect(controller.debounceRate).toBe(500)
  })
  it('Allows override of the debounce rate per field', () => {
    store.commit('forms/initForm', {
      name: 'example',
      fields: {
        name: {value: 'Fox', errors: ['Too cool.'], disabled: true, debounce: 200},
        age: {value: 30},
      },
      debounce: 500,
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'name'}})
    expect(controller.debounceRate).toBe(200)
  })
  it('Validates a field', async() => {
    formRegistry.validators.min = min
    store.commit('forms/initForm', {
      name: 'example',
      fields: {
        name: {value: 'Fox', disabled: true},
        age: {
          value: 20,
          validators: [
            {name: 'min', args: [30]},
            {name: 'min', args: [25, 'You\'ve got to be at least 25.']},
          ],
          errors: ['Old error'],
        },
      },
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'age'}})
    expect(controller.errors).toEqual(['Old error'])
    controller.forceValidate()
    await flushPromises()
    expect(controller.errors).toEqual(['Too low.', 'You\'ve got to be at least 25.'])
  })
  it('Returns validators', async() => {
    formRegistry.validators.min = min
    const validators = [
      {name: 'min', args: [30]},
      {name: 'min', args: [25, 'You\'ve got to be at least 25.']},
    ]
    store.commit('forms/initForm', {
      name: 'example',
      fields: {
        name: {value: 'Fox', disabled: true},
        age: {
          value: 20,
          validators,
          errors: ['Old error'],
        },
      },
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'age'}})
    expect(controller.validators).toEqual(validators)
  })
  it('Updates a field without validation', () => {
    formRegistry.validators.min = min
    store.commit('forms/initForm', {
      name: 'example',
      fields: {
        name: {value: 'Fox', disabled: true},
        age: {
          value: 30,
          validators: [
            {name: 'min', args: [30]},
            {name: 'min', args: [25, 'You\'ve got to be at least 25.']},
          ],
          errors: ['Old error'],
        },
      },
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'age'}})
    expect(controller.errors).toEqual(['Old error'])
    controller.update(20, false)
    expect(controller.errors).toEqual(['Old error'])
  })
  it('Exposes a field as a model', async() => {
    store.commit('forms/initForm', {
      name: 'example', fields: {name: {value: 'Fox'}}, endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'name'}})
    expect(state.example.fields.name.value).toBe('Fox')
    expect(controller.model).toBe('Fox')
    controller.model = 'Amber'
    await controller.$nextTick()
    expect(controller.model).toBe('Amber')
    expect(state.example.fields.name.value).toBe('Amber')
  })
  it('Runs async validators', async() => {
    formRegistry.validators.min = min
    formRegistry.asyncValidators.alwaysFail = alwaysFail
    store.commit('forms/initForm', {
      name: 'example',
      fields: {
        name: {value: 'Fox', disabled: true},
        age: {
          value: 20,
          validators: [
            {name: 'min', args: [30]},
            {name: 'min', args: [25, 'You\'ve got to be at least 25.']},
            {name: 'alwaysFail', args: ['test'], async: true},
          ],
          errors: ['Old error'],
        },
      },
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'age'}})
    controller.forceValidate()
    await flushPromises()
    expect(controller.errors).toEqual(['Too low.', 'You\'ve got to be at least 25.', 'I failed!'])
  })
  it('Gets and sets initial data on a field', async() => {
    formRegistry.validators.min = min
    formRegistry.asyncValidators.alwaysFail = alwaysFail
    store.commit('forms/initForm', {
      name: 'example',
      fields: {
        name: {value: 'Fox'},
        age: {
          value: 20,
        },
      },
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'age'}})
    expect(controller.initialData).toBe(20)
    controller.initialData = 15
    expect(state.example.fields.age.initialData).toBe(15)
  })
  it('Gives useful error message on unknown sync validator', async() => {
    store.commit('forms/initForm', {
      name: 'example',
      fields: {
        name: {value: 'Fox', disabled: true},
        age: {value: 30, validators: [{name: 'min', args: [30]}]},
      },
      endpoint: '/test/endpoint/',
    })
    formRegistry.validators.max = min
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'age'}})
    mockError.mockImplementationOnce(() => undefined)
    controller.forceValidate()
    expect(mockError).toHaveBeenCalledTimes(1)
    expect(mockError).toHaveBeenCalledWith(
      'Unregistered synchronous validator: ', 'min', '\n', 'Options are: ',
      ['max'])
  })
  it('Gives useful error message on unknown async validator', async() => {
    store.commit('forms/initForm', {
      name: 'example',
      fields: {
        name: {value: 'Fox', disabled: true},
        age: {value: 30, validators: [{name: 'min', async: true}, {name: 'alwaysSucceed', async: true}]},
      },
      endpoint: '/test/endpoint/',
    })
    formRegistry.asyncValidators.alwaysSucceed = alwaysSucceed
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'age'}})
    mockError.mockImplementationOnce(() => undefined)
    controller.forceValidate()
    expect(mockError).toHaveBeenCalledTimes(1)
    expect(mockError).toHaveBeenCalledWith(
      'Unregistered asynchronous validator: ', 'min', '\n', 'Options are: ',
      ['alwaysSucceed'])
  })
  it('Retrieves the parent form controller', () => {
    wrapper = shallowMount(Empty, {localVue, store})
    const controller = wrapper.vm.$getForm('example', {
      fields: {
        age: {value: 30},
      },
      endpoint: '/test/endpoint/',
    })
    const fieldController = controller.fields.age
    expect(fieldController.form).toBe(controller)
  })
  it('Correctly identifies an axios cancellation and ignores it.', async() => {
    mockTrace.mockImplementationOnce(() => undefined)
    const error = new Error('Request cancelled.');
    (error as any).__CANCEL__ = true
    axiosCatch(error)
    expect(mockTrace).toHaveBeenCalledTimes(0)
  })
  it('Correctly identifies a non-axios cancellation and complains about it.', async() => {
    mockTrace.mockImplementationOnce(() => undefined)
    const error = new Error('Failed!')
    axiosCatch(error)
    expect(mockTrace).toHaveBeenCalledTimes(1)
  })
  it('Resets the form', () => {
    wrapper = shallowMount(Empty, {localVue, store})
    const controller = wrapper.vm.$getForm('example', {
      fields: {
        age: {value: 30},
      },
      endpoint: '/test/endpoint/',
    })
    controller.fields.age.update(31)
    expect(controller.fields.age.value).toBe(31)
    controller.reset()
    expect(controller.fields.age.value).toBe(30)
  })
  it('Simplifies JSON rendering', () => {
    wrapper = shallowMount(Empty, {localVue, store})
    const controller = wrapper.vm.$getForm('example', {
      fields: {
        age: {value: 30},
      },
      endpoint: '/test/endpoint/',
    })
    expect(JSON.parse(JSON.stringify(controller))).toEqual({
      type: 'FormController', state: {age: 30}, name: 'example',
    })
    expect(JSON.parse(JSON.stringify(controller.fields.age))).toEqual({
      type: 'FieldController', state: 30, name: 'age',
    })
  })
  it('Makes a sane, consistent CSS name', () => {
    wrapper = shallowMount(Empty, {localVue, store})
    wrapper.vm.$getForm('example', {
      fields: {
        '@beep': {value: 30},
      },
      endpoint: '/test/endpoint/',
    })
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: '@beep'}})
    expect(controller.id).toBe('field-example__\\@beep')
  })
})
