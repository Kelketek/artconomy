import {ArtStore, createStore} from '@/store/index.ts'
import {formRegistry} from '../registry.ts'
import mockAxios from '@/specs/helpers/mock-axios.ts'
import {VueWrapper} from '@vue/test-utils'
import {registerValidators, required, simpleAsyncValidator, validateStatus} from '../validators.ts'
import flushPromises from 'flush-promises'
import MockDate from 'mockdate'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {cleanUp, mount, rq, vueSetup} from '@/specs/helpers/index.ts'
import {RootFormState} from '@/store/forms/types/RootFormState.ts'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

// These tests ought to be rewritten so we're not using these global changes somehow.

describe('Field validators', () => {
  let store: ArtStore
  let state: RootFormState
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    store = createStore()
    state = (store.state as any).forms as RootFormState
    registerValidators()
  })
  afterEach(() => {
    MockDate.reset()
    formRegistry.resetValidators()
    cleanUp(wrapper)
  })
  test('Verifies a required field is present.', async() => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm(
      'example',
      {fields: {name: {value: 'Fox'}, age: {value: 30}}, endpoint: '#'},
    ).fields.name
    expect(required(controller)).toEqual([])
    controller.update('')
    await flushPromises()
    expect(required(controller)).toEqual(['This field may not be blank.'])
  })
  test.each`
    email                  | result
    ${''}                  | ${[]}
    ${'test@example.com'}  | ${[]}
    ${'test'}              | ${['Emails must contain an @ in the middle.']}
    ${'@'}                 | ${['You must include the username in front of the @.']}
    ${'@stuff'}            | ${['You must include the username in front of the @.']}
    ${'test@'}             | ${['You must include the domain name after the @.']}
    ${'test @example.com'} | ${['Emails cannot have a space in the section before the @.']}
    ${'test@ example.com'} | ${['Emails cannot have a space in the section after the @.']}
    ${'test@example'}      | ${['Emails without a full domain are not supported. (Did you forget the .com?)']}
  `('should return $result when handed the email $email.', async({email, result}) => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm(
      'example',
      {fields: {email: {value: email, validators: [{name: 'email'}]}}, endpoint: '#'},
    ).fields.email
    controller.validate()
    controller.validate.flush()
    await flushPromises()
    expect(controller.errors).toEqual(result)
  })
  test.each`
    value1       | value2     | error             | result
    ${'test'}    | ${'test'}  | ${undefined}      | ${[]}
    ${'test'}    | ${'tess'}  | ${undefined}      | ${['Values do not match.']}
    ${'test'}    | ${'tess'}  | ${'Fail'}         | ${['Fail']}
  `('should return $result when matching $value1 and $value2 when message is set to $error.', async(
    {value1, value2, error, result},
  ) => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm('example', {
      endpoint: '',
      fields: {
        field1: {value: value1},
        field2: {value: value2, validators: [{name: 'matches', args: ['field1', error]}]},
      },
    }).fields.field2
    controller.validate()
    controller.validate.flush()
    await flushPromises()
    expect(controller.errors).toEqual(result)
  })
  test.each`
    status | result
    ${200} | ${true}
    ${204} | ${true}
    ${300} | ${false}
    ${500} | ${false}
    ${400} | ${true}
    ${403} | ${false}
    ${401} | ${false}
    ${104} | ${false}
  `('should designate the success status of $status as $result.', async({status, result}) => {
    expect(validateStatus(status)).toBe(result)
  })
  test('Generates an async validator that checks for a common error pattern.', async() => {
    const validator = simpleAsyncValidator('/api/profiles/form-validators/email/')
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm(
      'example2',
      {fields: {email: {value: 'test@example.com', validators: [{name: 'email'}]}}, endpoint: '#'},
    ).fields.email
    const source = new AbortController()
    validator(controller, source.signal).then()
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/api/profiles/form-validators/email/',
      'post',
      {email: 'test@example.com'},
      {signal: expect.any(Object), headers: {'Content-Type': 'application/json; charset=utf-8'}, validateStatus},
    ))
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
  })
  test('Returns errors from a generated async validator.', async() => {
    const validator = simpleAsyncValidator('/api/profiles/form-validators/email/')
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm(
      'example2',
      {fields: {email: {value: 'test@example.com', validators: [{name: 'email'}]}}, endpoint: '#'},
    ).fields.email
    const source = new AbortController()
    validator(controller, source.signal).then((data) => {
      expect(data).toEqual(['Test error1', 'Test error2'])
    })
    mockAxios.mockResponse({status: 400, data: {email: ['Test error1', 'Test error2']}})
    await flushPromises()
  })
  test('Returns an empty list from a generated async validator when field errors are not present.', async() => {
    const validator = simpleAsyncValidator('/api/profiles/form-validators/email/')
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm(
      'example2',
      {fields: {email: {value: 'test@example.com', validators: [{name: 'email'}]}}, endpoint: '#'},
    ).fields.email
    const source = new AbortController()
    validator(controller, source.signal).then((data) => {
      expect(data).toEqual([])
    })
    mockAxios.mockResponse({status: 400, data: {}})
    await flushPromises()
  })
  test.each`
    input       | result
    ${'#000'}   | ${['The color must be in the form of an RGB reference, like #000000 #FFFFFF or #c4c4c4.']}
    ${'asdf'}   | ${['The color must be in the form of an RGB reference, like #000000 #FFFFFF or #c4c4c4.']}
    ${'445534'} | ${['The color must be in the form of an RGB reference, like #000000 #FFFFFF or #c4c4c4.']}
    ${'    '}   | ${['The color must be in the form of an RGB reference, like #000000 #FFFFFF or #c4c4c4.']}
    ${'#5566ab'}| ${[]}
  `('Should validate a color reference', async({input, result}) => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm(
      'example',
      {fields: {color: {value: input, validators: [{name: 'colorRef'}]}}, endpoint: '#'},
    ).fields.color
    controller.validate()
    controller.validate.flush()
    await flushPromises()
    expect(controller.errors).toEqual(result)
  })
  test.each`
    input              | result
    ${'Hello there'}   | ${['Too long. Maximum length: 5.']}
    ${'Wat'}           | ${[]}
  `('Should validate a max length string', async({input, result}) => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm(
      'example',
      {fields: {name: {value: input, validators: [{name: 'maxLength', args: [5]}]}}, endpoint: '#'},
    ).fields.name
    controller.validate()
    controller.validate.flush()
    await flushPromises()
    expect(controller.errors).toEqual(result)
  })
  test.each`
    input              | result
    ${'Hello there'}   | ${[]}
    ${'Wat'}           | ${['Too short. Minimum length: 5.']}
  `('Should validate a min length string', async({input, result}) => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm(
      'example',
      {fields: {name: {value: input, validators: [{name: 'minLength', args: [5]}]}}, endpoint: '#'},
    ).fields.name
    controller.validate()
    controller.validate.flush()
    await flushPromises()
    expect(controller.errors).toEqual(result)
  })
  test.each`
    input         | result
    ${'5'}        | ${[]}
    ${'123434'}   | ${[]}
    ${'123s434'}  | ${['Numbers only, please.']}
    ${'1234.45'}  | ${[]}
    ${'-12.34'}   | ${[]}
  `('Validates a numeric entry', async({input, result}) => {
    wrapper = mount(Empty, vueSetup({store}))
    const controller = wrapper.vm.$getForm(
      'example',
      {fields: {items: {value: input, validators: [{name: 'numeric', args: [5]}]}}, endpoint: '#'},
    ).fields.items
    controller.validate()
    controller.validate.flush()
    await flushPromises()
    expect(controller.errors).toEqual(result)
  })
})
