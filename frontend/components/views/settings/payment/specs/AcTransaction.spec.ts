import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import AcTransaction from '@/components/views/settings/payment/AcTransaction.vue'
import {genCard, genUser} from '@/specs/helpers/fixtures.ts'
import {describe, expect, beforeEach, afterEach, test} from 'vitest'
import {setViewer} from '@/lib/lib.ts'
import type {Transaction} from '@/types/main'

let store: ArtStore
let wrapper: VueWrapper<any>

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
      rating_count: 1,
      is_staff: true,
      is_superuser: true,
      guest: false,
      artist_mode: true,
      taggable: true,
      verified_email: false,
    },
    payee: {
      id: 1,
      username: 'Fox',
      avatar_url: 'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
      stars: 4.0,
      rating_count: 1,
      is_staff: true,
      is_superuser: true,
      guest: false,
      artist_mode: true,
      taggable: true,
      verified_email: false,
    },
    amount: 14.0,
    remote_id: '72e6aab4-44ff-e911-811e-c292460a9c6d',
    created_on: '2019-11-04T14:50:24.084058-06:00',
    response_message: '',
    finalized_on: null,
    targets: [{
      last_four: '4567',
      type: 0,
      id: 1,
    }],
  }
}

describe('AcTransaction.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Displays a transaction as the payee', async() => {
    setViewer({ store, user: genUser() })
    wrapper = mount(AcTransaction, {
      ...vueSetup({store}),
      props: {
        transaction: genTransaction(),
        username: 'Fox',
        currentAccount: 300,
      },
    })
  })
  test('Displays a transaction as the payer', async() => {
    const user = genUser()
    user.username = 'Vulpes'
    setViewer({ store, user })
    wrapper = mount(AcTransaction, {
      ...vueSetup({store}),
      props: {
        transaction: genTransaction(),
        username: 'Vulpes',
        currentAccount: 300,
      },
    })
  })
  test('Displays a transaction as a transfer between accounts', () => {
    const user = genUser()
    setViewer({store, user})
    const transaction = genTransaction()
    transaction.payer = transaction.payee
    wrapper = mount(AcTransaction, {
      ...vueSetup({store}),
      props: {
        transaction,
        username: 'Fox',
        currentAccount: 301,
      },
    })
  })
  test('Displays a transaction as the payer with a null payee', async() => {
    const user = genUser()
    user.username = 'Vulpes'
    setViewer({ store, user })
    const transaction = genTransaction()
    transaction.payee = null
    wrapper = mount(AcTransaction, {
      ...vueSetup({store}),
      props: {
        transaction,
        username: 'Vulpes',
        currentAccount: 300,
      },
    })
  })
  test('Handles a card', async() => {
    setViewer({ store, user: genUser() })
    const transaction = genTransaction()
    transaction.card = genCard()
    wrapper = mount(AcTransaction, {
      ...vueSetup({store}),
      props: {
        transaction,
        username: 'Fox',
        currentAccount: 300,
      },
    })
  })
  test('Handles a transaction link', async() => {
    const user = genUser()
    user.is_superuser = true
    setViewer({ store, user })
    const transaction = genTransaction()
    transaction.card = genCard()
    wrapper = mount(AcTransaction, {
      ...vueSetup({store}),
      props: {
        transaction,
        username: 'Fox',
        currentAccount: 300,
      },
    })
    const vm = wrapper.vm as any
    expect(vm.transactionLink).toEqual(`/admin/sales/transactionrecord/${transaction.id}/`)
  })
  test('Does not give a transaction link if the user is not a superuser', async() => {
    const user = genUser()
    user.is_superuser = false
    setViewer({ store, user })
    const transaction = genTransaction()
    transaction.card = genCard()
    wrapper = mount(AcTransaction, {
      ...vueSetup({store}),
      props: {
        transaction,
        username: 'Fox',
        currentAccount: 300,
      },
    })
    const vm = wrapper.vm as any
    expect(vm.transactionLink).toBe(null)
  })
})
