import {useViewer} from '@/mixins/viewer.ts'
import {AnyUser, ProfileController} from '@/store/profiles/controller.ts'
import {SingleController} from '@/store/singles/controller.ts'
import Order from '@/types/Order.ts'
import Deliverable from '@/types/Deliverable.ts'
import {ListController} from '@/store/lists/controller.ts'
import Submission from '@/types/Submission.ts'
import {baseCardSchema, baseInvoiceSchema, paypalTokenToUrl} from '@/lib/lib.ts'
import DeliverableViewSettings from '@/types/DeliverableViewSettings.ts'
import {ViewerType, ViewerTypeValue} from '@/types/ViewerType.ts'
import {User} from '@/store/profiles/types/User.ts'
import Revision from '@/types/Revision.ts'
import LinkedCharacter from '@/types/LinkedCharacter.ts'
import LineItem from '@/types/LineItem.ts'
import LinkedReference from '@/types/LinkedReference.ts'
import {addBusinessDays, isAfter} from 'date-fns'
import {LocationQueryValue, useRoute} from 'vue-router'
import {DeliverableStatus} from '@/types/DeliverableStatus.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import {computed, nextTick, watch} from 'vue'
import {useProfile} from '@/store/profiles/hooks.ts'
import {parseISO} from '@/lib/otherFormatters.ts'
import Comment from '@/types/Comment.ts'
import {OrderProps} from '@/types/OrderProps.ts'

export interface DeliverableProps extends OrderProps {
  deliverableId: string|number,
}

export const ensureHandler = (handler: ProfileController, user: User, loadProfile?: boolean) => {
  if (!handler.user.x) {
    handler.user.setX(user)
    handler.user.ready = true
    nextTick(handler.user.get).then()
  }
  if (loadProfile) {
    /* istanbul ignore next */
    if (!handler.artistProfile.x) {
      nextTick(handler.artistProfile.get).then()
    }
  }
}


const getInitialViewSetting = (isStaff: boolean, setting: LocationQueryValue | LocationQueryValue[]) => {
  if (!isStaff) {
    return false
  }
  switch (setting) {
    case ('Seller'): {
      return ViewerType.SELLER
    }
    case ('Buyer'): {
      return ViewerType.BUYER
    }
    case ('Staff'): {
      return ViewerType.STAFF
    }
  }
}

const getOutput = (user: AnyUser|null, outputsController: ListController<Submission>) => {
  if (!user) {
    return null
  }
  const outputs = outputsController.list.filter((x: SingleController<Submission>) => {
    const submission = x.x as Submission
    return submission.owner.username === user.username
  })
  if (!outputs.length) {
    return null
  }
  return outputs[0].x as Submission
}

/*
This composable is used by all deliverable routes. Some crucial operations only occur in DeliverableDetail as it is the
host component and so can avoid running commands repeatedly, such as setting the buyer, seller, and arbitrator handlers.
*/
export const useDeliverable = <T extends DeliverableProps>(props: T) => {
  const route = useRoute()
  const {isStaff, rawViewerName} = useViewer()
  const prefix = computed(() => {
    return `order${props.orderId}__deliverable${props.deliverableId}`
  })

  const orderUrl = computed(() => {
    return `/api/sales/order/${props.orderId}/`
  })

  const url = computed(() => {
    return `/api/sales/order/${props.orderId}/deliverables/${props.deliverableId}/`
  })

  const viewSettings = useSingle<DeliverableViewSettings>(
    `${prefix.value}__viewSettings`,
    {
      x: {
        viewerType: getInitialViewSetting(isStaff.value, route.query.view_as) || ViewerType.UNSET,
        showAddSubmission: false,
        showPayment: false,
        characterInitItems: [],
        showAddDeliverable: false,
      },
      endpoint: '#',
    },
  )
  viewSettings.ready = true

  const statusEndpoint = (append: string) => () => {
    stateChange.endpoint = `${url.value}${append}/`
    return stateChange.submitThen(deliverable.setX)
  }

  const buyerHandler = useProfile(`__order__${props.orderId}__buyer`, {})
  const sellerHandler = useProfile(`__order__${props.orderId}__seller`, {})
  const arbitratorHandler = useProfile(`__order__${props.orderId}__arbitrator`, {})

  const buyer = computed(() => {
    return buyerHandler.user.x
  })

  const seller = computed(() => {
    return sellerHandler.user.x as User
  })

  const viewMode = computed({
    get() {
      return viewSettings.model.viewerType
    },
    set(viewerType: ViewerTypeValue) {
      viewSettings.model.viewerType = viewerType
    }
  })

  const order = useSingle<Order>(`order${props.orderId}`, {endpoint: orderUrl.value})
  const deliverable = useSingle<Deliverable>(
    `${prefix.value}`, {
      endpoint: url.value,
      socketSettings: {
        appLabel: 'sales',
        modelName: 'Deliverable',
        serializer: 'DeliverableSerializer',
      },
    },
  )
  const comments = useList<Comment>(
    `${prefix.value}__comments`, {
      endpoint: `/api/lib/comments/sales.Deliverable/${props.deliverableId}/`,
      reverse: true,
      grow: true,
      params: {size: 5},
    })
  const characters = useList<LinkedCharacter>(
    `${prefix.value}__characters`, {
      endpoint: `${url.value}characters/`,
      paginated: false,
    },
  )
  const revisions = useList<Revision>(
    `${prefix.value}__revisions`, {
      endpoint: `${url.value}revisions/`,
      paginated: false,
    },
  )
  const references = useList<LinkedReference>(
    `${prefix.value}__references`, {
      endpoint: `${url.value}references/`,
      paginated: false,
    },
  )
  // Used as wrapper for state change events.
  const stateChange = useForm(`${prefix.value}__stateChange`, {
    endpoint: url.value,
    fields: {},
  })
  const orderEmail = useForm(`order${props.orderId}__email`, {
    endpoint: `${url.value}invite/`,
    fields: {},
  })
  // Temporary endpoint URL-- we replace this in the setHandlers function upon loading the deliverable.
  const schema = baseCardSchema(`${url.value}pay/`)
  schema.fields = {
    ...schema.fields,
    card_id: {value: null},
    service: {value: null},
    amount: {value: 0},
    remote_id: {value: ''},
    cash: {value: false},
  }
  const paymentForm = useForm(`${prefix.value}__payment`, schema)
  const lineItems = useList<LineItem>(`${prefix.value}__lineItems`, {
    endpoint: `${url.value}line-items/`,
    paginated: false,
    socketSettings: {
      appLabel: 'sales',
      modelName: 'LineItem',
      serializer: 'LineItemSerializer',
      list: {
        appLabel: 'sales',
        modelName: 'Deliverable',
        pk: `${props.deliverableId}`,
        listName: 'line_items',
      },
    },
  })
  lineItems.firstRun().then()
  const outputUrl = computed(() => `${url.value}outputs/`)
  const outputs = useList<Submission>(`${prefix.value}__outputs`, {endpoint: outputUrl.value})
  const addSubmission = useForm(`${prefix.value}__addSubmission`, {
    endpoint: outputUrl.value,
    fields: {
      title: {value: ''},
      caption: {value: ''},
      private: {value: false},
      tags: {value: []},
      revision: {value: null},
      comments_disabled: {value: false},
    },
  })
  const invoiceSchema = baseInvoiceSchema(`/api/sales/order/${props.orderId}/deliverables/`)
  invoiceSchema.fields.characters = {value: []}
  invoiceSchema.fields.references = {value: []}
  invoiceSchema.fields.name = {value: 'New Deliverable'}
  const newInvoice = useForm(`${prefix.value}__addDeliverable`, invoiceSchema)

  const escrow = computed(() => {
    /* istanbul ignore if */
    if (!deliverable.x) {
      return false
    }
    return deliverable.x.escrow_enabled
  })

  const disputeWindow = computed(() => {
    let date: Date
    /* istanbul ignore if */
    if (!deliverable.x) {
      return false
    }
    if (!deliverable.x.trust_finalized) {
      return false
    }
    if (deliverable.x.auto_finalize_on) {
      date = parseISO(deliverable.x.auto_finalize_on)
    } else {
      return false
    }
    return isAfter(date, new Date())
  })

  const deliveryDate = computed(() => {
    let time: Date
    if (!deliverable.x) {
      return null
    }
    if (deliverable.x.paid_on) {
      time = parseISO(deliverable.x.paid_on)
    } else {
      return null
    }
    return addBusinessDays(time, Math.ceil(expectedTurnaround.value))
  })

  const expectedTurnaround = computed(() => {
    /* istanbul ignore if */
    if (!deliverable.x) {
      return NaN
    }
    if (!product.value) {
      return deliverable.x.expected_turnaround + deliverable.x.adjustment_expected_turnaround
    }
    if (is(DeliverableStatus.NEW, DeliverableStatus.PAYMENT_PENDING)) {
      return product.value.expected_turnaround + deliverable.x.adjustment_expected_turnaround
    }
    return deliverable.x.expected_turnaround + deliverable.x.adjustment_expected_turnaround
  })

  const is = (...status: number[]) => {
    /* istanbul ignore if */
    if (!(deliverable && deliverable.x)) {
      return false
    }
    return status.indexOf(deliverable.x.status) !== -1
  }

  const updateDeliverable = (revisedDeliverable: Deliverable) => {
    deliverable.updateX(revisedDeliverable)
    viewSettings.patchers.showPayment.model = false
  }

  const editable = computed(() => {
    return (is(DeliverableStatus.NEW) || is(DeliverableStatus.WAITING))
  })

  const isBuyer = computed(() => {
    if (viewMode.value === ViewerType.BUYER) {
      return true
    }
    if (viewMode.value !== ViewerType.UNSET) {
      return false
    }
    return buyer.value && buyer.value.username === rawViewerName.value
  })

  const isSeller = computed(() => {
    if (viewMode.value === ViewerType.SELLER) {
      return true
    }
    if (viewMode.value !== ViewerType.UNSET) {
      return false
    }
    return seller.value && seller.value.username === rawViewerName.value
  })

  const taskWeight = computed(() => {
    if (!deliverable.x) {
      return 0
    }
    if ((!product.value || !is(DeliverableStatus.NEW))) {
      return deliverable.x.task_weight + deliverable.x.adjustment_task_weight
    }
    return product.value.task_weight + deliverable.x.adjustment_task_weight
  })

  const isArbitrator = computed(() => {
    return viewMode.value === ViewerType.STAFF
  })

  const isInvolved = computed(() => {
    return isBuyer.value || isSeller.value || isArbitrator.value
  })

  const paypalUrl = computed(() => {
    if (!deliverable.x) {
      return ''
    }
    return paypalTokenToUrl(deliverable.x.paypal_token, isSeller.value)
  })


  const product = computed(() => {
    /* istanbul ignore if */
    if (!deliverable.x) {
      return null
    }
    if (!deliverable.x.product) {
      return null
    }
    return deliverable.x.product
  })

  const revisionCount = computed(() => {
    /* istanbul ignore if */
    if (!deliverable.x) {
      return NaN
    }
    if (!product.value) {
      return deliverable.x.revisions + deliverable.x.adjustment_revisions
    }
    if (is(DeliverableStatus.NEW) || is(DeliverableStatus.PAYMENT_PENDING)) {
      return product.value.revisions + deliverable.x.adjustment_revisions
    }
    return deliverable.x.revisions + deliverable.x.adjustment_revisions
  })

  const archived = computed(() => {
    return is(DeliverableStatus.COMPLETED) || is(DeliverableStatus.REFUNDED) || is(DeliverableStatus.CANCELLED)
  })

  const name = computed(() => {
    if (!product.value) {
      return '(Custom Project)'
    }
    return product.value.name
  })
  // @ts-ignore
  window.deliverable = deliverable

  watch(() => deliverable.x?.id, (newId?: number) => {
    if (!newId) {
      return
    }
    const ourDeliverable = deliverable.x as Deliverable
    const order = ourDeliverable.order
    if (order.buyer) {
      // This order has a buyer.
      ensureHandler(buyerHandler, order.buyer)
    }
    ensureHandler(sellerHandler, order.seller, true)
    paymentForm.endpoint = `/api/sales/invoice/${ourDeliverable.invoice}/pay/`
    /* istanbul ignore if */
    if (viewMode.value !== ViewerType.UNSET) {
      return
    }
    if (buyer.value && buyer.value.username === rawViewerName.value) {
      viewMode.value = ViewerType.BUYER
    } else if (seller.value && seller.value.username === rawViewerName.value) {
      viewMode.value = ViewerType.SELLER
    }
  }, {immediate: true})

  const buyerSubmission = computed(() => getOutput(buyer.value, outputs))
  const sellerSubmission = computed(() => getOutput(seller.value, outputs))
  return {
    viewSettings,
    order,
    deliverable,
    name,
    product,
    comments,
    characters,
    revisions,
    references,
    stateChange,
    newInvoice,
    addSubmission,
    outputs,
    paymentForm,
    lineItems,
    orderEmail,
    buyer,
    seller,
    isBuyer,
    isSeller,
    isArbitrator,
    isInvolved,
    revisionCount,
    archived,
    arbitratorHandler,
    sellerHandler,
    buyerHandler,
    sellerSubmission,
    buyerSubmission,
    statusEndpoint,
    is,
    editable,
    viewMode,
    url,
    escrow,
    paypalUrl,
    prefix,
    disputeWindow,
    deliveryDate,
    expectedTurnaround,
    taskWeight,
    updateDeliverable,
  }
}
