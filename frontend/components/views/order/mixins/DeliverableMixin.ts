import {Component, mixins, Prop, Watch} from 'vue-facing-decorator'
import Viewer, {useViewer} from '@/mixins/viewer.ts'
import {AnyUser, ProfileController} from '@/store/profiles/controller.ts'
import {SingleController} from '@/store/singles/controller.ts'
import Order from '@/types/Order.ts'
import Deliverable from '@/types/Deliverable.ts'
import {ListController} from '@/store/lists/controller.ts'
import Submission from '@/types/Submission.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import {baseCardSchema, baseInvoiceSchema, paypalTokenToUrl} from '@/lib/lib.ts'
import DeliverableViewSettings from '@/types/DeliverableViewSettings.ts'
import {VIEWER_TYPE} from '@/types/VIEWER_TYPE.ts'
import {User} from '@/store/profiles/types/User.ts'
import Revision from '@/types/Revision.ts'
import LinkedCharacter from '@/types/LinkedCharacter.ts'
import LineItem from '@/types/LineItem.ts'
import LinkedReference from '@/types/LinkedReference.ts'
import Pricing from '@/types/Pricing.ts'
import {addBusinessDays, isAfter} from 'date-fns'
import {LocationQueryValue, useRoute} from 'vue-router'
import {DeliverableStatus} from '@/types/DeliverableStatus.ts'
import {usePricing} from '@/mixins/PricingAware.ts'
import Reference from '@/types/Reference.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import {computed, getCurrentInstance, nextTick, Raw, ref, watch} from 'vue'
import {useProfile} from '@/store/profiles/hooks.ts'
import {Character} from '@/store/characters/types/Character.ts'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import {parseISO} from '@/lib/otherFormatters.ts'

/*

This mixin is used by all deliverable routes. Some crucial operations only occur in DeliverableDetail as it is the host
component and so can avoid running commands repeatedly, such as setting the buyer, seller, and arbitrator handlers.

 */
@Component
export default class BaseDeliverableMixin extends mixins(Viewer) {
  @Prop({required: true})
  public orderId!: string

  @Prop({required: true})
  public deliverableId!: string

  @Prop({required: true})
  public baseName!: string

  public buyerHandler: ProfileController | null = null
  public sellerHandler: ProfileController = null as unknown as ProfileController
  public arbitratorHandler: ProfileController | null = null
  public order: SingleController<Order> = null as unknown as SingleController<Order>
  public viewSettings = null as unknown as SingleController<DeliverableViewSettings>
  public deliverable: SingleController<Deliverable> = null as unknown as SingleController<Deliverable>
  public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
  public characters: ListController<LinkedCharacter> = null as unknown as ListController<LinkedCharacter>
  public comments: ListController<Comment> = null as unknown as ListController<Comment>
  public revisions: ListController<Revision> = null as unknown as ListController<Revision>
  public references: ListController<LinkedReference> = null as unknown as ListController<LinkedReference>
  public outputs: ListController<Submission> = null as unknown as ListController<Submission>
  public stateChange: FormController = null as unknown as FormController
  public paymentForm: FormController = null as unknown as FormController
  public addSubmission: FormController = null as unknown as FormController
  public newInvoice: FormController = null as unknown as FormController
  public orderEmail: FormController = null as unknown as FormController
  public lineItems: ListController<LineItem> = null as unknown as ListController<LineItem>
  public WAITING = DeliverableStatus.WAITING
  public NEW = DeliverableStatus.NEW
  public PAYMENT_PENDING = DeliverableStatus.PAYMENT_PENDING
  public QUEUED = DeliverableStatus.QUEUED
  public IN_PROGRESS = DeliverableStatus.IN_PROGRESS
  public REVIEW = DeliverableStatus.REVIEW
  public CANCELLED = DeliverableStatus.CANCELLED
  public DISPUTED = DeliverableStatus.DISPUTED
  public COMPLETED = DeliverableStatus.COMPLETED
  public REFUNDED = DeliverableStatus.REFUNDED
  public LIMBO = DeliverableStatus.LIMBO
  public MISSED = DeliverableStatus.MISSED

  public get product() {
    /* istanbul ignore if */
    if (!this.deliverable.x) {
      return null
    }
    if (!this.deliverable.x.product) {
      return null
    }
    return this.deliverable.x.product
  }

  public is(status: number) {
    /* istanbul ignore if */
    if (!(this.deliverable && this.deliverable.x)) {
      return false
    }
    return this.deliverable.x.status === status
  }

  public getOutput(user: User | null) {
    if (!user) {
      return null
    }
    const outputs = this.outputs.list.filter((x: SingleController<Submission>) => {
      const submission = x.x as Submission
      return submission.owner.username === user.username
    })
    if (!outputs.length) {
      return null
    }
    return outputs[0].x as Submission
  }

  public get buyerSubmission() {
    return this.getOutput(this.buyer as User)
  }

  public get sellerSubmission() {
    return this.getOutput(this.seller as User)
  }

  public get paypalUrl() {
    if (!this.deliverable.x) {
      return ''
    }
    return paypalTokenToUrl(this.deliverable.x.paypal_token, !!this.isSeller)
  }

  public ensureHandler(handler: ProfileController, user: User, loadProfile?: boolean) {
    ensureHandler(handler, user, loadProfile)
  }

  @Watch('deliverable.x.id')
  public setHandlers(newId: number | null) {
    /* istanbul ignore if */
    if (!newId) {
      return
    }
    const deliverable = this.deliverable.x as Deliverable
    const order = deliverable.order
    if (order.buyer) {
      // This order has a buyer.
      this.buyerHandler = this.$getProfile(order.buyer.username, {})
      this.ensureHandler(this.buyerHandler, order.buyer)
    }
    this.sellerHandler = this.$getProfile(order.seller.username, {})
    this.ensureHandler(this.sellerHandler, order.seller, true)
    this.paymentForm.endpoint = `/api/sales/invoice/${deliverable.invoice}/pay/`
    /* istanbul ignore if */
    if (this.viewMode !== VIEWER_TYPE.UNSET) {
      return
    }
    if (this.buyer && this.buyer.username === this.rawViewerName) {
      this.viewMode = VIEWER_TYPE.BUYER
    } else if (this.seller && this.seller.username === this.rawViewerName) {
      this.viewMode = VIEWER_TYPE.SELLER
    }
  }

  public get revisionCount() {
    const deliverable = this.deliverable.x as Deliverable
    /* istanbul ignore if */
    if (!this.order) {
      return NaN
    }
    if (!this.product) {
      return deliverable.revisions + deliverable.adjustment_revisions
    }
    if (this.is(this.NEW) || this.is(this.PAYMENT_PENDING)) {
      return this.product.revisions + deliverable.adjustment_revisions
    }
    return deliverable.revisions + deliverable.adjustment_revisions
  }

  public get deliveryDate() {
    let time: Date
    const deliverable = this.deliverable.x
    if (!deliverable) {
      return null
    }
    if (deliverable.paid_on) {
      time = parseISO(deliverable.paid_on)
    } else {
      time = new Date()
    }
    return addBusinessDays(time, Math.ceil(this.expectedTurnaround))
  }

  public get disputeWindow() {
    let date: Date
    /* istanbul ignore if */
    if (!this.deliverable.x) {
      return false
    }
    if (!this.deliverable.x.trust_finalized) {
      return false
    }
    if (this.deliverable.x.auto_finalize_on) {
      date = parseISO(this.deliverable.x.auto_finalize_on)
    } else {
      return false
    }
    return isAfter(date, new Date())
  }

  public get escrow() {
    const deliverable = this.deliverable.x as Deliverable
    /* istanbul ignore if */
    if (!deliverable) {
      return false
    }
    return deliverable.escrow_enabled
  }

  public get expectedTurnaround() {
    const deliverable = this.deliverable.x as Deliverable
    /* istanbul ignore if */
    if (!this.order) {
      return NaN
    }
    if (!this.product) {
      return deliverable.expected_turnaround + deliverable.adjustment_expected_turnaround
    }
    if (this.is(this.NEW) || this.is(this.PAYMENT_PENDING)) {
      return this.product.expected_turnaround + deliverable.adjustment_expected_turnaround
    }
    return deliverable.expected_turnaround + deliverable.adjustment_expected_turnaround
  }

  public get taskWeight() {
    const deliverable = this.deliverable.x as Deliverable
    if ((!this.product || !this.is(this.NEW))) {
      return deliverable.task_weight + deliverable.adjustment_task_weight
    }
    return this.product.task_weight + deliverable.adjustment_task_weight
  }

  public statusEndpoint(append: string) {
    return () => {
      this.stateChange.endpoint = `${this.url}${append}/`
      return this.stateChange.submitThen(this.deliverable.setX)
    }
  }

  public get archived() {
    return this.is(this.COMPLETED) || this.is(this.REFUNDED) || this.is(this.CANCELLED)
  }

  public get orderUrl() {
    return `/api/sales/order/${this.orderId}/`
  }

  public get url() {
    return `/api/sales/order/${this.orderId}/deliverables/${this.deliverableId}/`
  }

  public get prefix() {
    return `order${this.orderId}__deliverable${this.deliverableId}`
  }

  public get buyer() {
    if (!this.buyerHandler) {
      return null
    }
    return this.buyerHandler.user.x
  }

  public get seller() {
    /* istanbul ignore if */
    if (!this.sellerHandler) {
      return null
    }
    return this.sellerHandler.user.x as User
  }

  public get viewMode() {
    // Race condition in a subcomponent watcher lets this jump in before it's set.
    if (this.viewSettings === null) {
      return VIEWER_TYPE.UNSET
    }
    return this.viewSettings.model.viewerType
  }

  public set viewMode(viewerType: VIEWER_TYPE) {
    this.viewSettings.model.viewerType = viewerType
  }

  public get arbitrator() {
    /* istanbul ignore if */
    if (!this.arbitratorHandler) {
      return null
    }
    return this.arbitratorHandler.user.x
  }

  public get isBuyer() {
    if (this.viewMode === VIEWER_TYPE.BUYER) {
      return true
    }
    if (this.viewMode !== VIEWER_TYPE.UNSET) {
      return false
    }
    return this.buyer && this.buyer.username === this.rawViewerName
  }

  public get isSeller() {
    if (this.viewMode === VIEWER_TYPE.SELLER) {
      return true
    }
    if (this.viewMode !== VIEWER_TYPE.UNSET) {
      return false
    }
    return this.seller && this.seller.username === this.rawViewerName
  }

  public get isArbitrator() {
    return this.viewMode === VIEWER_TYPE.STAFF
  }

  public get isInvolved() {
    return this.isBuyer || this.isSeller || this.isArbitrator
  }

  public get editable() {
    return (this.is(this.NEW) || this.is(this.WAITING))
  }

  public updateDeliverable(deliverable: Deliverable) {
    this.deliverable.updateX(deliverable)
    this.viewSettings.patchers.showPayment.model = false
  }

  public get name() {
    if (!this.product) {
      return '(Custom Project)'
    }
    return this.product.name
  }

  public getInitialViewSetting(setting: LocationQueryValue | LocationQueryValue[]) {
    if (!this.isStaff) {
      return false
    }
    switch (setting) {
      case ('Seller'): {
        return VIEWER_TYPE.SELLER
      }
      case ('Buyer'): {
        return VIEWER_TYPE.BUYER
      }
      case ('Staff'): {
        return VIEWER_TYPE.STAFF
      }
    }
  }

  public created() {
    this.viewSettings = this.$getSingle(
      `${this.prefix}__viewSettings`, {
        x: {
          viewerType: this.getInitialViewSetting(this.$route.query.view_as) || VIEWER_TYPE.UNSET,
          showAddSubmission: false,
          showPayment: false,
          characterInitItems: [],
          showAddDeliverable: false,
        },
        endpoint: '#',
      },
    )
    this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/pricing-info/'})
    this.pricing.get()
    this.viewSettings.ready = true
    this.order = this.$getSingle(`order${this.orderId}`, {endpoint: this.orderUrl})
    this.deliverable = this.$getSingle(
      `${this.prefix}`, {
        endpoint: this.url,
        socketSettings: {
          appLabel: 'sales',
          modelName: 'Deliverable',
          serializer: 'DeliverableSerializer',
        },
      },
    )
    this.comments = this.$getList(
      `${this.prefix}__comments`, {
        endpoint: `/api/lib/comments/sales.Deliverable/${this.deliverableId}/`,
        reverse: true,
        grow: true,
        params: {size: 5},
      })
    this.characters = this.$getList(
      `${this.prefix}__characters`, {
        endpoint: `${this.url}characters/`,
        paginated: false,
      },
    )
    this.revisions = this.$getList(
      `${this.prefix}__revisions`, {
        endpoint: `${this.url}revisions/`,
        paginated: false,
      },
    )
    this.references = this.$getList(
      `${this.prefix}__references`, {
        endpoint: `${this.url}references/`,
        paginated: false,
      },
    )
    // Used as wrapper for state change events.
    this.stateChange = this.$getForm(`${this.prefix}__stateChange`, {
      endpoint: this.url,
      fields: {},
    })
    this.orderEmail = this.$getForm(`order${this.orderId}__email`, {
      endpoint: `${this.url}invite/`,
      fields: {},
    })
    // Temporary endpoint URL-- we replace this in the setHandlers function upon loading the deliverable.
    const schema = baseCardSchema(`${this.url}pay/`)
    schema.fields = {
      ...schema.fields,
      card_id: {value: null},
      service: {value: null},
      amount: {value: 0},
      remote_id: {value: ''},
      cash: {value: false},
    }
    this.paymentForm = this.$getForm(`${this.prefix}__payment`, schema)
    this.lineItems = this.$getList(`${this.prefix}__lineItems`, {
      endpoint: `${this.url}line-items/`,
      paginated: false,
      socketSettings: {
        appLabel: 'sales',
        modelName: 'LineItem',
        serializer: 'LineItemSerializer',
        list: {
          appLabel: 'sales',
          modelName: 'Deliverable',
          pk: `${this.deliverableId}`,
          listName: 'line_items',
        },
      },
    })
    this.lineItems.firstRun()
    const outputUrl = `${this.url}outputs/`
    this.outputs = this.$getList(`${this.prefix}__outputs`, {endpoint: outputUrl})
    this.addSubmission = this.$getForm(`${this.prefix}__addSubmission`, {
      endpoint: outputUrl,
      fields: {
        title: {value: ''},
        caption: {value: ''},
        private: {value: false},
        tags: {value: []},
        revision: {value: null},
        comments_disabled: {value: false},
      },
    })
    const invoiceSchema = baseInvoiceSchema(`/api/sales/order/${this.orderId}/deliverables/`)
    invoiceSchema.fields.characters = {value: []}
    invoiceSchema.fields.references = {value: []}
    invoiceSchema.fields.name = {value: 'New Deliverable'}
    this.newInvoice = this.$getForm(`${this.prefix}__addDeliverable`, invoiceSchema)
  }
}


export interface DeliverableProps {
  orderId: string|number,
  deliverableId: string|number,
  baseName: 'Order' | 'Sale' | 'Case'
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
      return VIEWER_TYPE.SELLER
    }
    case ('Buyer'): {
      return VIEWER_TYPE.BUYER
    }
    case ('Staff'): {
      return VIEWER_TYPE.STAFF
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
        viewerType: getInitialViewSetting(isStaff.value, route.query.view_as) || VIEWER_TYPE.UNSET,
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
    set(viewerType: VIEWER_TYPE) {
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
  const lineItems = useList(`${prefix.value}__lineItems`, {
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

  const is = (status: number) => {
    /* istanbul ignore if */
    if (!(deliverable && deliverable.x)) {
      return false
    }
    return deliverable.x.status === status
  }

  const updateDeliverable = (revisedDeliverable: Deliverable) => {
    deliverable.updateX(revisedDeliverable)
    viewSettings.patchers.showPayment.model = false
  }

  const editable = computed(() => {
    return (is(DeliverableStatus.NEW) || is(DeliverableStatus.WAITING))
  })

  const isBuyer = computed(() => {
    if (viewMode.value === VIEWER_TYPE.BUYER) {
      return true
    }
    if (viewMode.value !== VIEWER_TYPE.UNSET) {
      return false
    }
    return buyer.value && buyer.value.username === rawViewerName.value
  })

  const isSeller = computed(() => {
    if (viewMode.value === VIEWER_TYPE.SELLER) {
      return true
    }
    if (viewMode.value !== VIEWER_TYPE.UNSET) {
      return false
    }
    return seller.value && seller.value.username === rawViewerName.value
  })

  const isArbitrator = computed(() => {
    return viewMode.value === VIEWER_TYPE.STAFF
  })

  const isInvolved = computed(() => {
    return isBuyer.value || isSeller.value || isArbitrator.value
  })

  const paypalUrl = computed(() => {
    if (!deliverable.x) {
      return ''
    }
    return paypalTokenToUrl(deliverable.x.paypal_token, !!isSeller.value)
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
    if (viewMode.value !== VIEWER_TYPE.UNSET) {
      return
    }
    if (buyer.value && buyer.value.username === rawViewerName.value) {
      viewMode.value = VIEWER_TYPE.BUYER
    } else if (seller.value && seller.value.username === rawViewerName.value) {
      viewMode.value = VIEWER_TYPE.SELLER
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
    updateDeliverable,
  }
}
