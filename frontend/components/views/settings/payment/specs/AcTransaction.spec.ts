import {cleanUp, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import AcTransaction from '@/components/views/settings/payment/AcTransaction.vue'
import {genCard, genUser} from '@/specs/helpers/fixtures'
import Transaction from '@/types/Transaction'

const localVue = vueSetup()
let store: ArtStore

function genTransaction(): Transaction {
  return {
    id: 'cqdBIZItTV2A',
    source: 303,
    destination: 301,
    status: 2,
    category: 406,
    card: null,
    payer: {
      id: 1,
      username: 'Vulpes',
      avatar_url: 'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
      stars: 4.0,
      is_staff: true,
      is_superuser: true,
      guest: false,
      artist_mode: true,
      taggable: true,
    },
    payee: {
      id: 1,
      username: 'Fox',
      avatar_url: 'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
      stars: 4.0,
      is_staff: true,
      is_superuser: true,
      guest: false,
      artist_mode: true,
      taggable: true,
    },
    amount: 14.0,
    remote_id: '72e6aab4-44ff-e911-811e-c292460a9c6d',
    created_on: '2019-11-04T14:50:24.084058-06:00',
    response_message: '',
    finalized_on: null,
    target: {last_four: '4567', type: 0, id: 1},
  }
}

describe('AcTransaction.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp()
  })
  it('Displays a transaction as the payee', () => {
    setViewer(store, genUser())
    mount(AcTransaction, {
      localVue, store, propsData: {transaction: genTransaction(), username: 'Fox', currentAccount: 300},
    })
  })
  it('Displays a transaction as the payer', () => {
    const user = genUser()
    user.username = 'Vulpes'
    setViewer(store, user)
    mount(AcTransaction, {
      localVue, store, propsData: {transaction: genTransaction(), username: 'Vulpes', currentAccount: 300},
    })
  })
  it('Displays a transaction as a transfer between accounts', () => {
    const user = genUser()
    setViewer(store, user)
    const transaction = genTransaction()
    transaction.payer = transaction.payee
    mount(AcTransaction, {
      localVue, store, propsData: {transaction, username: 'Fox', currentAccount: 301},
    })
  })
  it('Displays a transaction as the payer with a null payee', () => {
    const user = genUser()
    user.username = 'Vulpes'
    setViewer(store, user)
    const transaction = genTransaction()
    transaction.payee = null
    mount(AcTransaction, {
      localVue, store, propsData: {transaction, username: 'Vulpes', currentAccount: 300},
    })
  })
  it('Handles a card', () => {
    setViewer(store, genUser())
    const transaction = genTransaction()
    transaction.card = genCard()
    mount(AcTransaction, {
      localVue, store, propsData: {transaction, username: 'Fox', currentAccount: 300},
    })
  })
})
