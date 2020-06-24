<template>
  <v-col>
    <v-card>
      <ac-link :to="deliverableLink">
        <ac-asset :asset="deliverable.display" thumb-name="thumbnail" />
      </ac-link>
      <v-card-text>
        <v-row dense>
          <v-col cols="12">
            <ac-link :to="deliverableLink">
              {{deliverable.name}}</ac-link>
          </v-col>
          <v-col cols="12" class="text-center">
            <ac-deliverable-status :deliverable="deliverable" />
          </v-col>
          <v-col cols="12">
            Created on <span v-text="formatDateTime(order.created_on)" />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-col>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import Deliverable from '@/types/Deliverable'
import Order from '@/types/Order'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAsset from '@/components/AcAsset.vue'
import AcDeliverableStatus from '@/components/AcDeliverableStatus.vue'
import Formatting from '@/mixins/formatting'
@Component({
  components: {AcDeliverableStatus, AcOrderStatus: AcDeliverableStatus, AcAsset, AcLink},
})
export default class AcDeliverablePreview extends mixins(Formatting) {
  @Prop({required: true})
  public deliverable!: Deliverable
  @Prop({required: true})
  public order!: Order
  @Prop({required: true})
  public scope!: string

  public get deliverableLink() {
    return {name: `${this.scope}Deliverable`, params: {orderId: this.order.id, deliverableId: this.deliverable.id}}
  }
}
</script>
