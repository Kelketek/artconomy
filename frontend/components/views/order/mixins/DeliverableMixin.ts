import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {Mutation} from 'vuex-class'
import {Prop, Watch} from 'vue-property-decorator'
import {ProfileController} from '@/store/profiles/controller'
import {SingleController} from '@/store/singles/controller'
import Order from '@/types/Order'
import Deliverable from '@/types/Deliverable'
import {ListController} from '@/store/lists/controller'
import Submission from '@/types/Submission'
import {FormController} from '@/store/forms/form-controller'
import {baseCardSchema, baseInvoiceSchema, parseISO} from '@/lib/lib'
import {LineTypes} from '@/types/LineTypes'
import DeliverableViewSettings from '@/types/DeliverableViewSettings'
import {VIEWER_TYPE} from '@/types/VIEWER_TYPE'
import {User} from '@/store/profiles/types/User'
import Revision from '@/types/Revision'
import LinkedCharacter from '@/types/LinkedCharacter'
import LineItem from '@/types/LineItem'
import LinkedReference from '@/types/LinkedReference'
import Pricing from '@/types/Pricing'
import {addBusinessDays, isAfter} from 'date-fns'
/*

This mixin is used by all deliverable routes. Some crucial operations only occur in DeliverableDetail as it is the host
component and so can avoid running commands repeatedly, such as setting the buyer, seller, and arbitrator handlers.

 */
@Component
export default class DeliverableMixin extends mixins(Viewer) {
  @Mutation('supportDialog') public setSupport: any
  @Prop({required: true})
  public orderId!: string

  @Prop({required: true})
  public deliverableId!: string

  @Prop({required: true})
  public baseName!: string

  public buyerHandler: ProfileController|null = null
  public sellerHandler: ProfileController = null as unknown as ProfileController
  public arbitratorHandler: ProfileController|null = null
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
  public tipForm: FormController = null as unknown as FormController
  public addSubmission: FormController = null as unknown as FormController
  public newInvoice: FormController = null as unknown as FormController
  public orderEmail: FormController = null as unknown as FormController
  public lineItems: ListController<LineItem> = null as unknown as ListController<LineItem>
  public WAITING = 0
  public NEW = 1
  public PAYMENT_PENDING = 2
  public QUEUED = 3
  public IN_PROGRESS = 4
  public REVIEW = 5
  public CANCELLED = 6
  public DISPUTED = 7
  public COMPLETED = 8
  public REFUNDED = 9

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
    if (!this.deliverable.x) {
      return false
    }
    return this.deliverable.x.status === status
  }

  public getOutput(user: User|null) {
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
    return outputs[0]
  }

  public get buyerSubmission() {
    return this.getOutput(this.buyer as User)
  }

  public get sellerSubmission() {
    return this.getOutput(this.seller as User)
  }

  public ensureHandler(handler: ProfileController, user: User, loadProfile?: boolean) {
    if (!handler.user.x) {
      handler.user.setX(user)
      handler.user.ready = true
      // Make sure we get the full info since it's cached for other stuff.
      handler.user.get()
    }
    if (loadProfile) {
      /* istanbul ignore next */
      if (!handler.artistProfile.x) {
        handler.artistProfile.get()
      }
    }
  }

  @Watch('deliverable.x.id')
  public setHandlers(newId: number|null) {
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
    return !deliverable.escrow_disabled
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
      this.stateChange.submitThen(this.deliverable.setX)
    }
  }

  public get archived() {
    return this.is(this.COMPLETED) || this.is(this.REFUNDED) || this.is(this.CANCELLED)
  }

  public get orderUrl() {
    return `/api/sales/v1/order/${this.orderId}/`
  }

  public get url() {
    return `/api/sales/v1/order/${this.orderId}/deliverables/${this.deliverableId}/`
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
    return this.sellerHandler.user.x
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
    if (this.viewMode === VIEWER_TYPE.STAFF) {
      return true
    }
    return false
  }

  public get isInvolved() {
    return this.isBuyer || this.isSeller || this.isArbitrator
  }

  public updateDeliverable(deliverable: Deliverable) {
    this.deliverable.updateX(deliverable)
    this.viewSettings.model.showPayment = false
  }

  public get name() {
    if (!this.product) {
      return '(Custom Project)'
    }
    return this.product.name
  }

  public created() {
    this.viewSettings = this.$getSingle(
      `${this.prefix}__viewSettings`, {
        x: {
          viewerType: VIEWER_TYPE.UNSET,
          showAddSubmission: false,
          showPayment: false,
          characterInitItems: [],
          showAddDeliverable: false,
        },
        endpoint: '#',
      },
    )
    this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/v1/pricing-info/'})
    this.pricing.get()
    this.viewSettings.ready = true
    this.order = this.$getSingle(`order${this.orderId}`, {endpoint: this.orderUrl})
    this.deliverable = this.$getSingle(
      `${this.prefix}`, {
        endpoint: this.url,
        socketSettings: {
          appLabel: 'sales',
          modelName: 'Deliverable',
          serializer: 'DeliverableViewSerializer',
        },
      },
    )
    this.comments = this.$getList(
      `${this.prefix}__comments`, {
        endpoint: `/api/lib/v1/comments/sales.Deliverable/${this.deliverableId}/`,
        reverse: true,
        grow: true,
        pageSize: 5,
      })
    this.characters = this.$getList(
      `${this.prefix}__characters`, {endpoint: `${this.url}characters/`, paginated: false},
    )
    this.revisions = this.$getList(
      `${this.prefix}__revisions`, {endpoint: `${this.url}revisions/`, paginated: false},
    )
    this.references = this.$getList(
      `${this.prefix}__references`, {endpoint: `${this.url}references/`, paginated: false},
    )
    // Used as wrapper for state change events.
    this.stateChange = this.$getForm(`${this.prefix}__stateChange`, {endpoint: this.url, fields: {}})
    this.orderEmail = this.$getForm(`order${this.orderId}__email`, {endpoint: `${this.url}invite/`, fields: {}})
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
    this.tipForm = this.$getForm(`${this.prefix}__tip`, {
      endpoint: `${this.url}line-items/`,
      fields: {
        amount: {value: 0, validators: [{name: 'numeric'}]},
        percentage: {value: 0},
        type: {value: LineTypes.TIP},
      },
    })
    const outputUrl = `${this.url}outputs/`
    this.outputs = this.$getList(`${this.prefix}__outputs`, {endpoint: outputUrl})
    this.addSubmission = this.$getForm(`${this.prefix}__addSubmission`, {
      endpoint: outputUrl,
      fields: {
        title: {value: ''},
        caption: {value: ''},
        private: {value: false},
        tags: {value: []},
        comments_disabled: {value: false},
      },
    })
    const invoiceSchema = baseInvoiceSchema(`/api/sales/v1/order/${this.orderId}/deliverables/`)
    invoiceSchema.fields.characters = {value: []}
    invoiceSchema.fields.references = {value: []}
    invoiceSchema.fields.name = {value: 'New Deliverable'}
    this.newInvoice = this.$getForm(`${this.prefix}__addDeliverable`, invoiceSchema)
  }
}
