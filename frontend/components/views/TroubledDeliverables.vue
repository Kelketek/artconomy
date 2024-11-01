<template>
  <v-container>
    <h1>Troubled Deliverables</h1>
    <ac-paginated :list="troubledDeliverables">
      <template v-slot:default>
        <v-simple-table>
          <template v-slot:default>
            <thead>
            <tr>
              <th>Deliverable ID</th>
              <th>Order ID</th>
              <th>Status</th>
              <th>Created On</th>
              <th>Paid On</th>
              <th>Buyer</th>
              <th>Seller</th>
              <th>Actions</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="deliverable in troubledDeliverables.list" :key="deliverable.x!.id">
              <td>{{deliverable.x!.id}}</td>
              <td>{{deliverable.x!.order.id}}</td>
              <td>
                <ac-deliverable-status :deliverable="deliverable.x!"/>
              </td>
              <td>{{formatDateTime(deliverable.x!.created_on)}}</td>
              <td>{{deliverable.x!.paid_on && formatDateTime(deliverable.x!.paid_on)}}</td>
              <td>
                <ac-avatar :user="deliverable.x!.order.buyer" v-if="deliverable.x!.order.buyer"/>
                <span v-else>{{deliverable.x!.order.customer_email}}</span></td>
              <td>
                <ac-avatar :user="deliverable.x!.order.seller"/>
              </td>
              <td>
                <ac-link
                    :to="{name: 'CaseDeliverableOverview', params: {orderId: `${deliverable.x!.order.id}`, deliverableId: `${deliverable.x!.id}`, username: viewer!.username}}"
                    v-if="deliverable.x!.arbitrator && deliverable.x!.arbitrator.username === viewer!.username">
                  View
                </ac-link>
                <v-btn @click="claimDeliverable(deliverable)" v-else small variant="flat">Claim</v-btn>
              </td>
            </tr>
            </tbody>
          </template>
        </v-simple-table>
      </template>
    </ac-paginated>
  </v-container>
</template>

<script setup lang="ts">
import {useViewer} from '@/mixins/viewer.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcDeliverableStatus from '@/components/AcDeliverableStatus.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {artCall} from '@/lib/lib.ts'
import {SingleController} from '@/store/singles/controller.ts'
import AcAvatar from '@/components/AcAvatar.vue'
import {useList} from '@/store/lists/hooks.ts'
import {formatDateTime} from '@/lib/otherFormatters.ts'
import type {Deliverable} from '@/types/main'

const {viewer} = useViewer()
const troubledDeliverables = useList<Deliverable>('troubledDeliverables', {endpoint: '/api/sales/reports/troubled-deliverables/'})
const claimDeliverable = async (deliverable: SingleController<Deliverable>) => {
  return artCall({
    url: `/api/sales/order/${deliverable.x!.order.id}/deliverables/${deliverable.x!.id}/claim/`,
    method: 'post',
  }).then(deliverable.updateX)
}
</script>
