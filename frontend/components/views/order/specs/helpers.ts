import { createRouter, createWebHistory, RouteLocation } from "vue-router"
import Empty from "@/specs/helpers/dummy_components/empty.ts"

export function deliverableRouter() {
  const props = (route: RouteLocation) => {
    return {
      ...route.params,
      baseName: "Order",
    }
  }
  return createRouter({
    history: createWebHistory(),
    routes: [
      {
        name: "Home",
        component: Empty,
        path: "/",
      },
      {
        name: "Login",
        component: Empty,
        path: "/login/",
        props: true,
      },
      {
        name: "Register",
        component: Empty,
        path: "/login/register/",
        props: true,
      },
      {
        name: "Order",
        component: Empty,
        path: "/orders/:username/order/:orderId/",
        props: true,
        children: [
          {
            name: "OrderDeliverable",
            component: Empty,
            path: "deliverables/:deliverableId/",
            props,
            children: [
              {
                name: "OrderDeliverableOverview",
                component: Empty,
                path: "overview",
                props,
              },
              {
                name: "OrderDeliverablePayment",
                component: Empty,
                path: "payment",
                props,
              },
              {
                name: "OrderDeliverableReferences",
                component: Empty,
                path: "references",
                props,
                children: [
                  {
                    name: "OrderDeliverableReference",
                    component: Empty,
                    path: ":referenceId",
                    props,
                  },
                ],
              },
              {
                name: "OrderDeliverableRevisions",
                component: Empty,
                path: "revisions",
                props,
                children: [
                  {
                    name: "OrderDeliverableRevision",
                    component: Empty,
                    path: ":revisionId",
                    props,
                  },
                ],
              },
            ],
          },
        ],
      },
      {
        name: "Sale",
        component: Empty,
        path: "/sales/:username/sale/:orderId/",
        props: true,
        children: [
          {
            name: "SaleDeliverable",
            component: Empty,
            path: "deliverables/:deliverableId/",
            props,
            children: [
              {
                name: "SaleDeliverableOverview",
                component: Empty,
                path: "overview",
                props,
              },
              {
                name: "SaleDeliverablePayment",
                component: Empty,
                path: "payment",
                props,
              },
              {
                name: "SaleDeliverableReferences",
                component: Empty,
                path: "reference",
                props,
                children: [
                  {
                    name: "SaleDeliverableReference",
                    component: Empty,
                    path: ":referenceId",
                    props,
                  },
                ],
              },
              {
                name: "SaleDeliverableRevisions",
                component: Empty,
                path: "revisions",
                props,
                children: [
                  {
                    name: "SaleDeliverableRevision",
                    component: Empty,
                    path: ":revisionId",
                    props,
                  },
                ],
              },
            ],
          },
        ],
      },
      {
        name: "Submission",
        component: Empty,
        path: "/submissions/:submissionId/",
        props: true,
      },
      {
        name: "AboutUser",
        component: Empty,
        path: "/profiles/:username/about/",
        props: true,
      },
      {
        name: "Product",
        component: Empty,
        path: "/profiles/:username/products/:productId",
        props: true,
      },
      {
        name: "BuyAndSell",
        component: Empty,
        path: "/buy-and-sell/:question",
        props: true,
      },
      {
        name: "Settings",
        component: Empty,
        path: "/:username/settings/",
        props: true,
      },
      {
        name: "TermsOfService",
        component: Empty,
        path: "/terms/",
      },
      {
        name: "SessionSettings",
        component: Empty,
        path: "/settings/session/",
      },
      {
        name: "CommissionAgreement",
        component: Empty,
        path: "/agreement/",
      },
      {
        name: "Payout",
        component: Empty,
        path: "/:username/settings/payout/",
      },
    ],
  })
}
