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
                <ac-deliverable-status :deliverable="deliverable.x"/>
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

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer.ts'
import {ListController} from '@/store/lists/controller.ts'
import Deliverable from '@/types/Deliverable.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcDeliverablePreview from '@/components/AcDeliverablePreview.vue'
import AcDeliverableStatus from '@/components/AcDeliverableStatus.vue'
import Formatting from '@/mixins/formatting.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import {artCall} from '@/lib/lib.ts'
import {SingleController} from '@/store/singles/controller.ts'
import AcAvatar from '@/components/AcAvatar.vue'

@Component({
  components: {
    AcAvatar,
    AcLink,
    AcDeliverableStatus,
    AcDeliverablePreview,
    AcPaginated,
  },
})
class TroubledDeliverables extends mixins(Viewer, Formatting) {
  public troubledDeliverables = null as unknown as ListController<Deliverable>

  public claimDeliverable(deliverable: SingleController<Deliverable>) {
    return artCall({
      url: `/api/sales/order/${deliverable.x!.order.id}/deliverables/${deliverable.x!.id}/claim/`,
      method: 'post',
    }).then(deliverable.updateX)
  }

  public created() {
    this.troubledDeliverables = this.$getList('troubledDeliverables', {endpoint: '/api/sales/reports/troubled-deliverables/'})
  }
}

export default toNative(TroubledDeliverables)
</script>
