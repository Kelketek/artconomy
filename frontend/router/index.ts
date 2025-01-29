import {
  createRouter,
  createWebHistory,
  RouteLocation,
  RouteLocationNormalized,
  Router,
  RouteRecordRaw,
} from 'vue-router'
import {clearMetaTag, paramsKey, setCookie, setMetaContent} from '@/lib/lib.ts'
import {ArtStore} from '@/store/index.ts'
import {defineComponent, h} from 'vue'

const Reload = () => import('@/components/views/Reload.vue')
const Login = () => import('@/components/views/auth/Login.vue')
const Register = () => import('@/components/views/auth/Register.vue')
const Forgot = () => import('@/components/views/auth/Forgot.vue')
const AuthViews = () => import('@/components/views/auth/AuthViews.vue')
const ProductDetail = () => import('@/components/views/product/ProductDetail.vue')
const FAQ = () => import('@/components/views/faq/FAQ.vue')
const Submission = () => import('@/components/views/submission/SubmissionDetail.vue')
const Search = () => import('@/components/views/search/Search.vue')
const PasswordReset = () => import('@/components/views/PasswordReset.vue')
const SearchProducts = () => import('@/components/views/search/SearchProducts.vue')
const SearchCharacters = () => import('@/components/views/search/SearchCharacters.vue')
const SearchProfiles = () => import('@/components/views/search/SearchProfiles.vue')
const SearchSubmissions = () => import('@/components/views/search/SearchSubmissions.vue')
const ProductHints = () => import('@/components/views/search/hints/ProductHints.vue')
const SubmissionHints = () => import('@/components/views/search/hints/SubmissionHints.vue')
const CharacterHints = () => import('@/components/views/search/hints/CharacterHints.vue')
const ProfileHints = () => import('@/components/views/search/hints/ProfileHints.vue')
const Home = () => import('@/components/views/Home.vue')
const ProductExtra = () => import('@/components/views/search/extra/ProductExtra.vue')
const RedirectToViewer = () => import('@/components/views/RedirectToViewer.vue')
const RevisionDetail = () => import('@/components/views/order/deliverable/RevisionDetail.vue')
const ReferenceDetail = () => import('@/components/views/order/deliverable/ReferenceDetail.vue')
const DeliverableRevisions = () => import('@/components/views/order/deliverable/DeliverableRevisions.vue')
const DeliverableOverview = () => import('@/components/views/order/deliverable/DeliverableOverview.vue')
const DeliverablePayment = () => import('@/components/views/order/deliverable/DeliverablePayment.vue')
const DeliverableReferences = () => import('@/components/views/order/deliverable/DeliverableReferences.vue')
const DeliverableListing = () => import('@/components/views/order/OrderDetail.vue')
const DeliverableDetail = () => import('@/components/views/order/DeliverableDetail.vue')
const OrderList = () => import('@/components/views/orders/OrderList.vue')
const Orders = () => import('@/components/views/orders/Orders.vue')
const SessionSettings = () => import('@/components/views/SessionSettings.vue')
const Ratings = () => import('@/components/views/Ratings.vue')
const SubmissionExtra = () => import('@/components/views/search/extra/SubmissionExtra.vue')
const ReferralsAndTools = () => import('@/components/views/referrals/ReferralsAndTools.vue')
const LinksAndStats = () => import('@/components/views/referrals/LinksAndStats.vue')
const ArtistTools = () => import('@/components/views/landing/ArtistTools.vue')
const NewOrder = () => import('@/components/views/product/NewOrder.vue')
const Tools = () => import('@/components/views/referrals/Tools.vue')
const Upgrade = () => import('@/components/views/Upgrade.vue')
const WatchList = () => import('@/components/views/profile/WatchList.vue')
const ClaimOrder = () => import('@/components/views/ClaimOrder.vue')
const Premium = () => import('@/components/views/settings/Premium.vue')
const Redirect = () => import('@/components/views/Redirect.vue')
const ShieldCommissioner = () => import('@/components/views/landing/ShieldCommissioner.vue')
const AlwaysOpen = () => import('@/components/views/landing/AlwaysOpen.vue')
const ShieldArtist = () => import('@/components/views/landing/ShieldArtist.vue')
const About = () => import('@/components/views/faq/About.vue')
const BuyAndSell = () => import('@/components/views/faq/BuyAndSell.vue')
const Other = () => import('@/components/views/faq/Other.vue')
const ConversationsList = () => import('@/components/views/ConversationsList.vue')
const AboutUser = () => import('@/components/views/profile/AboutUser.vue')
const Products = () => import('@/components/views/profile/Products.vue')
const Characters = () => import('@/components/views/profile/Characters.vue')
const Gallery = () => import('@/components/views/profile/Gallery.vue')
const Watchlists = () => import('@/components/views/profile/Watchlists.vue')
const CharacterDetail = () => import('@/components/views/character/CharacterDetail.vue')
const Purchase = () => import('@/components/views/settings/payment/Purchase.vue')
const TransactionHistory = () => import('@/components/views/settings/payment/TransactionHistory.vue')
const Payout = () => import('@/components/views/settings/payment/Payout.vue')
const Settings = () => import('@/components/views/settings/Settings.vue')
const Social = () => import('@/components/views/settings/Social.vue')
const Options = () => import('@/components/views/settings/Options.vue')
const Email = () => import('@/components/views/settings/Email.vue')
const Artist = () => import('@/components/views/settings/Artist.vue')
const Credentials = () => import('@/components/views/settings/Credentials.vue')
const Avatar = () => import('@/components/views/settings/Avatar.vue')
const Payment = () => import('@/components/views/settings/payment/Payment.vue')
const CommissionAgreement = () => import('@/components/views/legal/CommissionAgreement.vue')
const RefundPolicy = () => import('@/components/views/legal/RefundPolicy.vue')
const TermsOfService = () => import('@/components/views/legal/TermsOfService.vue')
const PrivacyPolicy = () => import('@/components/views/legal/PrivacyPolicy.vue')
const Profile = () => import('@/components/views/profile/Profile.vue')
const Policies = () => import('@/components/views/legal/Policies.vue')
const Contact = () => import('@/components/views/Contact.vue')
const Store = () => import('@/components/views/store/Store.vue')
const ManageProducts = () => import('@/components/views/store/ManageProducts.vue')
const Reports = () => import('@/components/views/reports/Reports.vue')
const Journal = () => import('@/components/views/JournalDetail.vue')
const CharacterGallery = () => import('@/components/views/character/CharacterGallery.vue')
const NotFound = () => import('@/components/views/NotFound.vue')
const ConversationDetail = () => import('@/components/views/ConversationDetail.vue')
const SubmissionList = () => import('@/components/views/profile/SubmissionList.vue')
const ManageSubmissionList = () => import('@/components/views/profile/ManageSubmissionList.vue')
const ManageArtList = () => import('@/components/views/profile/ManageArtList.vue')
const Queue = () => import('@/components/views/Queue.vue')
const InvoiceDetail = () => import('@/components/views/invoice/InvoiceDetail.vue')
const VendorInvoices = () => import('@/components/views/VendorInvoices.vue')
const TableDashboard = () => import('@/components/views/table/TableDashboard.vue')
const TableProducts = () => import('@/components/views/table/TableProducts.vue')
const TableOrders = () => import('@/components/views/table/TableOrders.vue')
const TableInvoices = () => import('@/components/views/table/TableInvoices.vue')
const Invoices = () => import('@/components/views/settings/payment/Invoices.vue')
const TroubledDeliverables = () => import('@/components/views/TroubledDeliverables.vue')
const Promotable = () => import('@/components/views/Promotable.vue')
const ProductGallery = () => import('@/components/views/product/ProductGallery.vue')
const AcInvoiceProductSelection = () => import('@/components/views/orders/AcInvoiceProductSelection.vue')

const Empty = defineComponent({render: () => h('div'), data: () => ({})})

function orderViews() {
  const orderRoutes: RouteRecordRaw[] = []
  for (const baseName of ['Order', 'Sale', 'Case']) {
    const props = (route: RouteLocation) => {
      return {...route.params, baseName}
    }
    const category = baseName.toLowerCase()
    orderRoutes.push({
      name: baseName,
      path: `/${category}s/:username/${category}/:orderId/`,
      component: DeliverableListing,
      props,
      children: [{
        name: `${baseName}Deliverable`,
        path: 'deliverables/:deliverableId/',
        props,
        component: DeliverableDetail,
        children: [{
          name: `${baseName}DeliverableOverview`,
          path: 'overview/',
          props,
          component: DeliverableOverview,
        }, {
          name: `${baseName}DeliverableReferences`,
          path: 'references/',
          props,
          component: DeliverableReferences,
          children: [{
            name: `${baseName}DeliverableReference`,
            path: ':referenceId/',
            props,
            component: ReferenceDetail,
          }],
        }, {
          name: `${baseName}DeliverableRevisions`,
          path: 'revisions/',
          props,
          component: DeliverableRevisions,
          children: [{
            name: `${baseName}DeliverableRevision`,
            path: ':revisionId/',
            props,
            component: RevisionDetail,
          }],
        }, {
          name: `${baseName}DeliverablePayment`,
          path: 'payment/',
          props,
          component: DeliverablePayment,
        }],
      }],
    })
  }
  return orderRoutes
}

function orderLists() {
  const orderRoutes: RouteRecordRaw[] = []
  for (const baseName of ['Orders', 'Sales', 'Cases']) {
    const children: RouteRecordRaw[] = []
    let categories = ['current', 'archived', 'waiting', 'cancelled']
    if (baseName === 'Cases') {
      categories = ['current', 'archived']
    }
    const type = baseName.toLowerCase()
    for (const category of categories) {
      const routeName = category[0].toUpperCase() + category.slice(1) + baseName
      children.push({
        name: routeName,
        path: category,
        component: OrderList,
        props(route: RouteLocationNormalized) {
          return {
            username: route.params.username,
            category,
            type,
          }
        },
      })
    }
    orderRoutes.push({
      path: `/${type}/:username/`,
      name: baseName,
      component: Orders,
      children,
      props(route: RouteLocationNormalized) {
        return {
          username: route.params.username,
          baseName,
        }
      },
    })
  }
  return orderRoutes
}

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    props: true,
  },
  {
    path: '/Reload/:path',
    name: 'Reload',
    component: Reload,
  },
  {
    path: '/auth/',
    component: AuthViews,
    children: [{
      path: '',
      name: 'AuthViews',
      redirect: {name: 'Login'},
    }, {
      path: 'login/',
      name: 'Login',
      component: Login,
    }, {
      path: 'register/',
      name: 'Register',
      component: Register,
    }, {
      path: 'forgot/',
      name: 'Forgot',
      component: Forgot,
    }]
  },
  {
    path: '/set-password/:username/:resetToken/',
    props: true,
    component: PasswordReset,
  },
  {
    path: '/legal-and-policies/',
    name: 'Policies',
    component: Policies,
  },
  {
    path: '/legal-and-policies/commission-agreement/',
    name: 'CommissionAgreement',
    component: CommissionAgreement,
  },
  {
    path: '/legal-and-policies/refund-policy/',
    name: 'RefundPolicy',
    component: RefundPolicy,
  },
  {
    path: '/legal-and-policies/terms-of-service/',
    name: 'TermsOfService',
    component: TermsOfService,
  },
  {
    path: '/legal-and-policies/privacy-policy/',
    name: 'PrivacyPolicy',
    component: PrivacyPolicy,
  },
  {
    path: '/contact/',
    name: 'Contact',
    component: Contact,
  },
  {
    path: '/store/:username/',
    name: 'Store',
    component: Store,
    props(route: RouteLocation) {
      return {
        username: route.params.username,
      }
    },
    children: [
      {
        name: 'Product',
        path: 'product/:productId/',
        component: ProductDetail,
        props: true,
        children: [
          {
            name: 'NewOrder',
            path: 'order/:invoiceMode(invoice)?/',
            component: NewOrder,
            props: true,
          },
          {
            name: 'ProductGallery',
            path: 'gallery/',
            component: ProductGallery,
            props: true,
          },
        ],
      },
      {
        name: 'InvoiceByProduct',
        path: 'invoice-by-product/',
        component: AcInvoiceProductSelection,
        props: true,
      }
    ],
  },
  {
    path: '/store/:username/iframe/',
    name: 'StoreiFrame',
    component: Store,
    props(route: RouteLocation) {
      return {
        username: route.params.username,
        endpoint: `/api/sales/account/${route.params.username}/products/`,
        iFrame: true,
      }
    },
  },
  {
    path: '/faq/',
    name: 'FAQ',
    component: FAQ,
    children: [
      {
        name: 'About',
        path: 'about/:question?/',
        component: About,
        props: true,
      },
      {
        name: 'BuyAndSell',
        path: 'buying-and-selling/:question?/',
        component: BuyAndSell,
        props: true,
      },
      {
        name: 'Other',
        path: 'other/:question?/',
        component: Other,
        props: true,
      },
    ],
  },
  {
    path: '/my/:viewName/',
    name: 'MyView',
    component: RedirectToViewer,
    props: true,
  },
  {
    path: '/profile/:username/settings/',
    name: 'Settings',
    component: Settings,
    props: true,
    children: [
      {
        name: 'Login Details',
        path: 'credentials/',
        component: Credentials,
        props: true,
      },
      {
        name: 'Premium',
        path: 'premium/',
        component: Premium,
        props: true,
      },
      {
        name: 'Avatar',
        path: 'avatar/',
        component: Avatar,
        props: true,
      },
      {
        name: 'Social',
        path: 'social/',
        component: Social,
        props: true,
      },
      {
        name: 'Payment',
        path: 'payment/',
        component: Payment,
        props: true,
        children: [
          {
            name: 'Purchase',
            path: 'purchase/',
            component: Purchase,
            props: true,
          },
          {
            name: 'Payout',
            path: 'payout/',
            component: Payout,
            props: true,
          },
          {
            name: 'Invoices',
            path: 'invoices/',
            component: Invoices,
            props: true,
            children: [
              {
                path: ':invoiceId/',
                name: 'Invoice',
                component: InvoiceDetail,
                props: true,
              },
            ],
          },
          {
            name: 'TransactionHistory',
            path: 'transactions/',
            component: TransactionHistory,
            props: true,
          },
        ],
      },
      {
        name: 'Artist',
        path: 'artist/',
        component: Artist,
        props: true,
      },
      {
        name: 'Options',
        path: 'options/',
        component: Options,
        props: true,
      },
      {
        name: 'Email',
        path: 'email/',
        component: Email,
        props: true,
      },
    ],
  },
  {
    path: '/profile/:username/upgrade/',
    name: 'Upgrade',
    component: Upgrade,
    props: true,
  },
  {
    path: '/profile/:username/ratings/',
    name: 'Ratings',
    component: Ratings,
    props: true,
  },
  {
    path: '/profile/:username/queue/',
    name: 'Queue',
    component: Queue,
    props: true,
  },
  {
    path: '/profile/:username/invoice/:invoiceId/',
    name: 'InvoiceDetail',
    component: InvoiceDetail,
    props: true,
  },
  {
    path: '/profile/:username/referrals/',
    name: 'ReferralsAndTools',
    component: ReferralsAndTools,
    props: true,
    children: [{
      name: 'LinksAndStats',
      path: 'links-and-stats/',
      component: LinksAndStats,
      props: true,
    }, {
      name: 'Tools',
      path: 'tools/',
      component: Tools,
      props: true,
    }],
  },
  {
    path: '/profile/:username/journals/:journalId/',
    name: 'Journal',
    component: Journal,
    props: true,
  },
  {
    path: '/profile/:username/characters/:characterName/',
    name: 'Character',
    component: CharacterDetail,
    props: true,
  },
  {
    path: '/profile/:username/characters/:characterName/gallery/',
    name: 'CharacterGallery',
    component: CharacterGallery,
    props: true,
  },
  {
    path: '/profile/:username/',
    name: 'Profile',
    component: Profile,
    props: true,
    children: [
      {
        path: 'about/',
        name: 'AboutUser',
        component: AboutUser,
        props: true,
      },
      {
        path: 'products/',
        name: 'Products',
        component: Products,
        props: true,
        children: [{
          name: 'ManageProducts',
          path: 'manage/',
          component: ManageProducts,
          props: true,
        }],
      },
      {
        path: 'characters/',
        name: 'Characters',
        component: Characters,
        props: true,
      },
      {
        path: 'gallery/',
        name: 'Gallery',
        component: Gallery,
        props: true,
        children: [{
          path: 'art',
          name: 'Art',
          component: SubmissionList,
          props(route: RouteLocation) {
            return {
              ...route.params,
              listName: 'art',
              endpoint: `/api/profiles/account/${route.params.username}/submissions/art/`,
              trackPages: true,
            }
          },
        }, {
          path: 'art/manage/',
          name: 'ManageArt',
          component: ManageArtList,
          props(route: RouteLocation) {
            return {
              ...route.params,
              listName: 'art',
              endpoint: `/api/profiles/account/${route.params.username}/submissions/art/management/`,
              trackPages: true,
            }
          },
        }, {
          path: 'collection/',
          name: 'Collection',
          component: SubmissionList,
          props(route: RouteLocation) {
            return {
              ...route.params,
              listName: 'collection',
              endpoint: `/api/profiles/account/${route.params.username}/submissions/collection/`,
              trackPages: true,
            }
          },
        }, {
          path: 'collection/manage/',
          name: 'ManageCollection',
          component: ManageSubmissionList,
          props(route: RouteLocation) {
            return {
              ...route.params,
              listName: 'collection',
              endpoint: `/api/profiles/account/${route.params.username}/submissions/collection/management/`,
              trackPages: true,
            }
          },
        }],
      },
      {
        path: 'favorites/',
        name: 'Favorites',
        component: SubmissionList,
        props(route: RouteLocation) {
          return {
            ...route.params,
            listName: 'favorites',
            endpoint: `/api/profiles/account/${route.params.username}/favorites/`,
            okStatuses: [403],
            failureMessage: "This user's favorites are hidden.",
          }
        },
      },
      {
        path: 'watchlists/',
        name: 'Watchlists',
        component: Watchlists,
        props: true,
        children: [{
          name: 'Watching',
          path: 'watching/',
          component: WatchList,
          props(route: RouteLocation) {
            return {
              ...route.params,
              nameSpace: 'watching',
              endpoint: `/api/profiles/account/${route.params.username}/watching/`,
            }
          },
        }, {
          name: 'Watchers',
          path: 'watchers/',
          component: WatchList,
          props(route: RouteLocation) {
            return {
              ...route.params,
              nameSpace: 'watchers',
              endpoint: `/api/profiles/account/${route.params.username}/watchers/`,
            }
          },
        }],
      },
    ],
  },
  {
    path: '/submissions/:submissionId/',
    name: 'Submission',
    component: Submission,
    props: true,
  },
  ...orderViews(),
  ...orderLists(),
  {
    path: '/claim-order/:orderId/:token/:deliverableId?/:next?/',
    name: 'ClaimOrder',
    component: ClaimOrder,
    props: true,
  },
  {
    path: '/search/',
    name: 'Search',
    component: Search,
    props: true,
    children: [{
      path: 'products/',
      name: 'SearchProducts',
      components: {
        default: SearchProducts,
        hints: ProductHints,
        extra: ProductExtra,
      },
      props: true,
    }, {
      path: 'submissions/',
      name: 'SearchSubmissions',
      components: {
        default: SearchSubmissions,
        hints: SubmissionHints,
        extra: SubmissionExtra,
      },
      props: true,
    }, {
      path: 'characters/',
      name: 'SearchCharacters',
      components: {
        default: SearchCharacters,
        hints: CharacterHints,
      },
      props: true,
    }, {
      path: 'profiles/',
      name: 'SearchProfiles',
      components: {
        default: SearchProfiles,
        hints: ProfileHints,
      },
      props: true,
    }],
  },
  {
    path: '/session/settings/',
    name: 'SessionSettings',
    component: SessionSettings,
  },
  {
    path: '/messages/:username/',
    name: 'Conversations',
    component: ConversationsList,
    props: true,
  },
  {
    path: '/messages/:username/:conversationId/',
    name: 'Conversation',
    component: ConversationDetail,
    props: true,
  },
  {
    path: '/reports/financial/:username/',
    name: 'Reports',
    props: true,
    component: Reports,
  },
  {
    path: '/reports/troubled-deliverables/',
    name: 'TroubledDeliverables',
    component: TroubledDeliverables,
  },
  {
    path: '/reports/promotable/',
    name: 'Promotable',
    component: Promotable,
  },
  {
    path: '/vendor-invoices/',
    name: 'VendorInvoices',
    component: VendorInvoices,
    children: [
      {
        path: ':invoiceId/',
        name: 'VendorInvoice',
        component: InvoiceDetail,
        props: true,
      }
    ],
  },
  {
    path: '/table/',
    name: 'TableDashboard',
    component: TableDashboard,
    children: [{
      path: 'products/',
      name: 'TableProducts',
      component: TableProducts,
    }, {
      path: 'orders/',
      name: 'TableOrders',
      component: TableOrders,
    }, {
      path: 'invoices/',
      name: 'TableInvoices',
      component: TableInvoices,
      children: [{
        path: ':username/:invoiceId/',
        name: 'TableInvoice',
        component: InvoiceDetail,
        props: true,
      }],
    }],
  },
  {
    path: '/landing/commission-safely-with-artconomy-shield/',
    name: 'LandingShieldCommissioner',
    component: ShieldCommissioner,
  },
  {
    path: '/landing/payment-guaranteed-with-artconomy-shield/',
    name: 'LandingShieldArtist',
    component: ShieldArtist,
  },
  {
    path: '/landing/always-open-for-commissions/',
    name: 'LandingAlwaysOpen',
    component: AlwaysOpen,
  },
  {
    path: '/landing/artist-tools/',
    name: 'LandingArtistTools',
    component: ArtistTools,
  },
  {
    path: '/who-is-open/',
    name: 'WhoIsOpenRedirect',
    component: Redirect,
    props: {route: '/search/products/'},
  },
  {
    path: '/recent-art/',
    name: 'RecentArtRedirect',
    component: Redirect,
    props: {route: '/search/submissions/'},
  },
  {
    path: '/empty/',
    name: 'Empty',
    component: Empty,
  },
  {
    path: '/:pathMatch(.*)',
    name: 'NotFound',
    component: NotFound,
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: async (to: RouteLocationNormalized, from: RouteLocationNormalized): Promise<void|{left: number, top: number}> => {
    if (!from || !to) {
      return
    }
    if ((from.name === to.name) || (from.matched[0] && (from.matched[0].name === to.matched[0].name))) {
      // Need to find cases of different IDs or usernames and blep them out.
      if (paramsKey(from.params) === paramsKey(to.params)) {
        return
      }
    }
    return {left: 0, top: 0}
  },
})

declare global {
  interface Window {
    _paq: Array<any[]>
  }
}

window._paq = window._paq || []

export function configureHooks(vueRouter: Router, store: ArtStore): void {
  vueRouter.beforeEach((to, from) => {
    clearMetaTag('prerender-status-code')
    store.commit('errors/setError', {response: {status: 0}})
    if ((String(to.name)).indexOf('iFrame') !== -1) {
      store.commit('setiFrame', true)
    }
    if (from.name !== to.name) {
      document.title = 'Artconomy-- The easy and safe way to commission art!'
      setMetaContent(
        'description',
        '',
        {content: 'Artconomy.com makes it easy, safe, and fun for you to get custom art of your original characters!'},
      )
    }
    if (to.query.referred_by) {
      setCookie('referredBy', to.query.referred_by)
    }
  })
}
