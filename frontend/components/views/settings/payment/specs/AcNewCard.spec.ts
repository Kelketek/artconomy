import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import Vuetify from 'vuetify'
import {ArtStore, createStore} from '@/store'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {listRegistry, Lists} from '@/store/lists/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {expectFields, fieldEl, flushPromises, rq, rs, setViewer, vueSetup, vuetifySetup} from '@/specs/helpers'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import mockAxios from '@/__mocks__/axios'
import {genUser} from '@/specs/helpers/fixtures'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import {FormController} from '@/store/forms/form-controller'
import {FieldController} from '@/store/forms/field-controller'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {baseCardSchema} from '@/lib'
import AcNewCard from '@/components/views/settings/payment/AcNewCard.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let cards: ListController<CreditCardToken>

function genList() {
  return [
    {id: 1, last_four: '1234', primary: true, type: 1, cvv_verified: true},
    {id: 2, last_four: '5432', primary: false, type: 2, cvv_verified: true},
    {id: 3, last_four: '4563', primary: false, type: 3, cvv_verified: true},
  ]
}

describe('AcNewCard.vue', () => {
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    singleRegistry.reset()
    listRegistry.reset()
    profileRegistry.reset()
    formRegistry.reset()
    mockAxios.reset()
    setViewer(store, genUser())
    const ccForm = mount(Empty, {localVue, store}).vm.$getForm('newCard', baseCardSchema('/test/'))
    wrapper = mount(
      AcNewCard, {
        localVue, store, sync: false, attachToDocument: true, propsData: {username: 'Fox', ccForm},
      })
    cards = (wrapper.vm as any).cards
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Fetches the initial data', async() => {
    const countriesRequest = mockAxios.lastReqGet()
    expect(mockAxios.get).toHaveBeenCalledWith(...[
      ...rq(`/api/lib/v1/countries/`, 'get', undefined),
    ])
    mockAxios.mockResponse(rs({US: 'United States', CA: 'Canada'}), countriesRequest)
    await flushPromises()
    await wrapper.vm.$nextTick()
    // expect(cards.list.length).toBe(3)
    expect((wrapper.vm as any).countryOptions).toEqual([
      {value: 'US', text: 'United States'},
      {value: 'CA', text: 'Canada'},
    ])
  })
  it('Has a card addition form', async() => {
    const ccForm = (wrapper.vm as any).ccForm as FormController
    wrapper.setProps({firstCard: true})
    await wrapper.vm.$nextTick()
    expectFields(
      ccForm.fields, ['first_name', 'last_name', 'zip', 'number', 'exp_date', 'cvv', 'country', 'make_primary']
    )
    // Doesn't show 'make primary' when there are no cards.
    Object.values(ccForm.fields).filter(
      (field) => ['make_primary', 'card_id'].indexOf(field.fieldName) === -1
    ).map((field: FieldController) => fieldEl(wrapper, field))
    expect(wrapper.find('#' + ccForm.fields.make_primary.id).exists()).toBe(false)
    wrapper.setProps({firstCard: false})
    await wrapper.vm.$nextTick()
    Object.values(ccForm.fields).filter((field) => field.fieldName !== 'card_id').map(
      (field: FieldController) => fieldEl(wrapper, field)
    )
  })
  it('Considers the card type unknown if it cannot be identified', async() => {
    const ccForm = (wrapper.vm as any).ccForm as FormController
    const num = fieldEl(wrapper, ccForm.fields.number)
    num.value = '999999'
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).ccType).toBe('unknown')
  })
  it('Identifies the credit card type', async() => {
    const ccForm = (wrapper.vm as any).ccForm as FormController
    ccForm.fields.number.update('4111111111111111', false)
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).ccType).toBe('visa')
  })
  it('Loads the correct hints for most cards', async() => {
    const ccForm = (wrapper.vm as any).ccForm as FormController
    ccForm.fields.number.update('4111111111111111', false)
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).hints).toEqual(
      {mask: '#### #### #### ####', cvv: '3 digit number on back of card'}
    )
  })
  it('Loads the correct hints for amex', async() => {
    const ccForm = (wrapper.vm as any).ccForm as FormController
    const num = fieldEl(wrapper, ccForm.fields.number)
    ccForm.fields.number.update('370000000000002', false)
    expect((wrapper.vm as any).ccType).toBe('amex')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).hints).toEqual(
      {mask: '#### ###### #####', cvv: '4 digit number on front of card'}
    )
  })
})
