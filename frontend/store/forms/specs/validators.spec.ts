import {ArtStore, createStore} from '../../index'
import Vue from 'vue'
import {FormControllers, formRegistry} from '../registry'
import mockAxios from '@/specs/helpers/mock-axios'
import Vuex from 'vuex'
import {createLocalVue, mount, shallowMount} from '@vue/test-utils'
import {artistRating, cardType, registerValidators, required, simpleAsyncValidator, validateStatus} from '../validators'
import {FieldController} from '../field-controller'
import flushPromises from 'flush-promises'
import axios from 'axios'
import MockDate from 'mockdate'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {setViewer} from '@/specs/helpers'
import {genArtistProfile, genUser} from '@/specs/helpers/fixtures'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {RootFormState} from '@/store/forms/types/RootFormState'

// These tests ought to be rewritten so we're not using these global changes somehow.
Vue.use(Vuex)
Vue.use(Profiles)
Vue.use(Singles)
Vue.use(FormControllers)
const localVue = createLocalVue()

describe('Field validators', () => {
  let store: ArtStore
  let state: RootFormState
  beforeEach(() => {
    formRegistry.reset()
    formRegistry.resetValidators()
    profileRegistry.reset()
    singleRegistry.reset()
    mockAxios.reset()
    store = createStore()
    state = (store.state as any).forms as RootFormState
    registerValidators()
  })
  afterEach(() => {
    MockDate.reset()
  })
  it('Verifies a required field is present.', async() => {
    store.commit('forms/initForm', {name: 'example', fields: {name: {value: 'Fox'}, age: {value: 30}}})
    const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'name'}})
    expect(required(controller)).toEqual([])
    controller.update('')
    await flushPromises()
    expect(required(controller)).toEqual(['This field may not be blank.'])
  })
  it.each`
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
  store.commit('forms/initForm', {
    name: 'example',
    fields: {email: {value: email, validators: [{name: 'email'}]}},
  })
  const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'email'}})
  controller.validate()
  controller.validate.flush()
  await flushPromises()
  expect(controller.errors).toEqual(result)
})
  it.each`
    value1       | value2     | error             | result
    ${'test'}    | ${'test'}  | ${undefined}      | ${[]}
    ${'test'}    | ${'tess'}  | ${undefined}      | ${['Values do not match.']}
    ${'test'}    | ${'tess'}  | ${'Fail'}         | ${['Fail']}
  `('should return $result when matching $value1 and $value2 when message is set to $error.', async(
  {value1, value2, error, result}
) => {
  const wrapper = shallowMount(Empty, {localVue, store})
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
  it.each`
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
  it('Generates an async validator that checks for a common error pattern.', async() => {
    const validator = simpleAsyncValidator('/api/profiles/v1/form-validators/email/')
    store.commit('forms/initForm', {
      name: 'example2',
      fields: {email: {value: 'test@example.com', validators: [{name: 'email'}]}},
    })
    const controller = new FieldController({store, propsData: {formName: 'example2', fieldName: 'email'}})
    const source = axios.CancelToken.source()
    validator(controller, source.token).then()
    expect(mockAxios.post).toHaveBeenCalledWith(
      '/api/profiles/v1/form-validators/email/',
      {email: 'test@example.com'},
      {cancelToken: expect.any(Object), headers: {'Content-Type': 'application/json; charset=utf-8'}, validateStatus}
    )
    expect(mockAxios.post).toHaveBeenCalledTimes(1)
  })
  it('Returns errors from a generated async validator.', async() => {
    const validator = simpleAsyncValidator('/api/profiles/v1/form-validators/email/')
    store.commit('forms/initForm', {
      name: 'example2',
      fields: {email: {value: 'test@example.com', validators: [{name: 'email'}]}},
    })
    const controller = new FieldController({store, propsData: {formName: 'example2', fieldName: 'email'}})
    const source = axios.CancelToken.source()
    validator(controller, source.token).then((data) => {
      expect(data).toEqual(['Test error1', 'Test error2'])
    })
    mockAxios.mockResponse({status: 400, data: {email: ['Test error1', 'Test error2']}})
    await flushPromises()
  })
  it('Returns an empty list from a generated async validator when field errors are not present.', async() => {
    const validator = simpleAsyncValidator('/api/profiles/v1/form-validators/email/')
    store.commit('forms/initForm', {
      name: 'example2',
      fields: {email: {value: 'test@example.com', validators: [{name: 'email'}]}},
    })
    const controller = new FieldController({store, propsData: {formName: 'example2', fieldName: 'email'}})
    const source = axios.CancelToken.source()
    validator(controller, source.token).then((data) => {
      expect(data).toEqual([])
    })
    mockAxios.mockResponse({status: 400, data: {}})
    await flushPromises()
  })
  it.each`
    date                   | result
    ${''}                  | ${[]}
    ${'0820'}              | ${['Please write the date in the format MM/YY, like 08/22.']}
    ${'0'}                 | ${['Please write the date in the format MM/YY, like 08/22.']}
    ${'12'}                | ${['Please write the date in the format MM/YY, like 08/22.']}
    ${'14/23'}              | ${['That is not a valid month.']}
    ${'@stuff'}            | ${['Please write the date in the format MM/YY, like 08/22.']}
    ${'05/02'}              | ${['This card has expired.']}
    ${'12/99'}              | ${[]}
  `('should return $result when handed the expiration date $date.', async({date, result}) => {
  MockDate.set('2019-6-19')
  store.commit('forms/initForm', {
    name: 'example',
    fields: {exp_date: {value: date, validators: [{name: 'cardExp'}]}},
  })
  const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'exp_date'}})
  controller.validate()
  controller.validate.flush()
  await flushPromises()
  expect(controller.errors).toEqual(result)
})
  it.each`
    cardNumber               | result
    ${'0'}                   | ${['That is not a valid card number. Please check the card.']}
    ${'4111111111111111'}    | ${[]}
    ${'4242424242424241'}    | ${['That is not a valid card number. Please check the card.']}
    ${'4111 1111 1111 1111'} | ${[]}
    ${'4111-1111-1111-1111'} | ${[]}
    ${'4242 4242 4242 4999'} | ${['That is not a valid card number. Please check the card.']}
  `('should return $result when handed the card number $cardNumber.', async({cardNumber, result}) => {
  store.commit('forms/initForm', {
    name: 'example',
    fields: {card_number: {value: cardNumber, validators: [{name: 'creditCard'}]}},
  })
  const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'card_number'}})
  controller.validate()
  controller.validate.flush()
  await flushPromises()
  expect(controller.errors).toEqual(result)
})
  it.each`
    cardNumber               | result
    ${'37000'}               | ${'amex'}
    ${'370000000000002'}     | ${'amex'}
    ${'5424'}                | ${'mastercard'}
    ${'5424000000000015'}    | ${'mastercard'}
    ${'42'}                  | ${'visa'}
    ${'4242424242424241'}    | ${'visa'}
    ${'6011'}                | ${'discover'}
    ${'6011000000000012'}    | ${'discover'}
    ${'3800000'}             | ${'diners'}
    ${'38000000000006'}      | ${'diners'}
    ${'853'}                 | ${'unknown'}
  `('should identify $result when handed the card number $cardNumber.', async({cardNumber, result}) => {
  expect(cardType(cardNumber)).toEqual(result)
})
  it.each`
    cardNumber               | cvv       | result
    ${'37000'}               | ${'025'}  | ${['Must be 4 digits long']}
    ${'370000000000002'}     | ${'1234'} | ${[]}
    ${'5424'}                | ${'vsd'}  | ${['Digits only, please']}
    ${'5424000000000015'}    | ${'001'}  | ${[]}
    ${'42'}                  | ${'0125'} | ${['Must be 3 digits long']}
  `('should return $result when handed the card number $cardNumber and the CVV $cvv.', async({cardNumber, cvv, result}
) => {
  store.commit('forms/initForm', {
    name: 'example',
    fields: {card_number: {value: cardNumber}, cvv: {value: cvv, validators: [{name: 'cvv'}]}},
  })
  const wrapper = mount(Empty, {localVue, store})
  const controller = wrapper.vm.$getForm('example', {
    fields: {
      card_number: {value: cardNumber},
      cvv: {value: cvv,
        validators: [{name: 'cvv', args: ['card_number']}],
      },
    },
    endpoint: '/',
  }).fields.cvv
  controller.validate()
  controller.validate.flush()
  await flushPromises()
  expect(controller.errors).toEqual(result)
})
  it.each`
    input       | result
    ${'#000'}   | ${['The color must be in the form of an RGB reference, like #000000 #FFFFFF or #c4c4c4.']}
    ${'asdf'}   | ${['The color must be in the form of an RGB reference, like #000000 #FFFFFF or #c4c4c4.']}
    ${'445534'} | ${['The color must be in the form of an RGB reference, like #000000 #FFFFFF or #c4c4c4.']}
    ${'    '}   | ${['The color must be in the form of an RGB reference, like #000000 #FFFFFF or #c4c4c4.']}
    ${'#5566ab'}| ${[]}
  `('Should validate a color reference', async({input, result}) => {
  store.commit('forms/initForm', {
    name: 'example',
    fields: {color: {value: input, validators: [{name: 'colorRef'}]}},
  })
  const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'color'}})
  controller.validate()
  controller.validate.flush()
  await flushPromises()
  expect(controller.errors).toEqual(result)
})
  it.each`
    input              | result
    ${'Hello there'}   | ${['Too long. Maximum length: 5.']}
    ${'Wat'}           | ${[]}
  `('Should validate a max length string', async({input, result}) => {
  store.commit('forms/initForm', {
    name: 'example',
    fields: {name: {value: input, validators: [{name: 'maxLength', args: [5]}]}},
  })
  const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'name'}})
  controller.validate()
  controller.validate.flush()
  await flushPromises()
  expect(controller.errors).toEqual(result)
})
  it.each`
    input              | result
    ${'Hello there'}   | ${[]}
    ${'Wat'}           | ${['Too short. Minimum length: 5.']}
  `('Should validate a min length string', async({input, result}) => {
  store.commit('forms/initForm', {
    name: 'example',
    fields: {name: {value: input, validators: [{name: 'minLength', args: [5]}]}},
  })
  const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'name'}})
  controller.validate()
  controller.validate.flush()
  await flushPromises()
  expect(controller.errors).toEqual(result)
})
  it.each`
    input         | result
    ${'5'}        | ${[]}
    ${'123434'}   | ${[]}
    ${'123s434'}  | ${['Numbers only, please.']}
    ${'1234.45'}  | ${[]}
    ${'-12.34'}   | ${[]}
  `('Validates a numeric entry', async({input, result}) => {
  store.commit('forms/initForm', {
    name: 'example',
    fields: {items: {value: input, validators: [{name: 'numeric', args: [5]}]}},
  })
  const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'items'}})
  controller.validate()
  controller.validate.flush()
  await flushPromises()
  expect(controller.errors).toEqual(result)
})
  it.each`
    input  | result
    ${'3'} | ${['The artist has not indicated that they wish to work with content at ' +
                'this rating level. Your request is likely to be denied.']}
    ${'2'} | ${[]}
    ${'1'} | ${[]}
  `('Identifies a rating which is over the maximum of an artist', async({input, result}) => {
  store.commit('forms/initForm', {
    name: 'example',
    fields: {rating: {value: input, validators: [{name: 'artistRating', args: ['Fox'], async: true}]}},
  })
  setViewer(store, genUser())
  const controller = new FieldController({store, propsData: {formName: 'example', fieldName: 'rating'}})
  const profileController = controller.$getProfile('Fox', {})
  const profile = genArtistProfile()
  profile.max_rating = 2
  await profileController.$nextTick()
  profileController.artistProfile.setX(profile)
  profileController.artistProfile.ready = true
  profileController.artistProfile.fetching = false
  controller.validate()
  controller.validate.flush()
  await flushPromises()
  expect(controller.errors).toEqual(result)
})
})
