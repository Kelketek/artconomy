<template>
  <v-container>
    <ac-paginated :list="troubledDeliverables">
      <template v-slot:header>
        <h1>Troubled Deliverables</h1>
      </template>
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
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="deliverable in troubledDeliverables.list" :key="deliverable.x.id">
                <td>{{deliverable.x.id}}</td>
                <td>{{deliverable.x.order.id}}</td>
                <td>
                  <ac-deliverable-status :deliverable="deliverable.x" />
                </td>
                <td>{{formatDateTime(deliverable.x.created_on)}}</td>
                <td>{{formatDateTime(deliverable.x.paid_on)}}</td>
                <td>
                  <ac-link :to="{name: 'CaseDeliverableOverview', params: {orderId: `${deliverable.x.order.id}`, deliverableId: `${deliverable.x.id}`, username: viewer.username}}" v-if="deliverable.x.arbitrator && deliverable.x.arbitrator.username === viewer.username">
                    View
                  </ac-link>
                  <v-btn @click="claimDeliverable(deliverable)" v-else small>Claim</v-btn>
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
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {ListController} from '@/store/lists/controller'
import Deliverable from '@/types/Deliverable'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcDeliverablePreview from '@/components/AcDeliverablePreview.vue'
import AcDeliverableStatus from '@/components/AcDeliverableStatus.vue'
import Formatting from '@/mixins/formatting'
import AcLink from '@/components/wrappers/AcLink.vue'
import {artCall} from '@/lib/lib'
import { SingleController } from '@/store/singles/controller'

@Component({
  components: {
    AcLink,
    AcDeliverableStatus,
    AcDeliverablePreview,
    AcPaginated,
  },
})
export default class TroubledDeliverables extends mixins(Viewer, Formatting) {
  public troubledDeliverables = null as unknown as ListController<Deliverable>

  public claimDeliverable(deliverable: SingleController<Deliverable>) {
    return artCall({url: `/api/sales/order/${deliverable.x!.order.id}/deliverables/${deliverable.x!.id}/claim/`, method: 'post'}).then(deliverable.updateX)
  }

  public created() {
    this.troubledDeliverables = this.$getList('troubledDeliverables', {endpoint: '/api/sales/reports/troubled-deliverables/'})
  }
}
</script>
