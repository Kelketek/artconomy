<template>
  <v-col v-if="order.x.seller">
      <v-card>
        <ac-link :to="order.x.default_path">
          <ac-asset
              :asset="order.x.display"
              thumb-name="thumbnail"
              :allow-preview="false"
          />
        </ac-link>
        <v-card-text>
          <v-row dense>
            <v-col cols="12">
              <ac-deliverable-status :deliverable="{status: order.x.status}" class="ma-1" />
            </v-col>
            <v-col cols="12">
              <ac-link :to="order.x.default_path">
                {{ name }}</ac-link>
              <span v-if="!isBuyer"> commissioned </span>by
              <ac-link v-if="isBuyer" :to="{name: 'Profile', params: {username: order.x.seller.username}}">
                {{ order.x.seller.username }}</ac-link>
              <ac-link v-else-if="order.x.buyer" :to="profileLink(order.x.buyer)">
                {{ deriveDisplayName(order.x.buyer.username) }}</ac-link>
              <span v-else>
                (Pending)
              </span>
            </v-col>
            <v-col cols="12" v-if="order.x.guest_email">
                <strong>{{order.x.guest_email}}</strong>
            </v-col>
            <v-col cols="12">
              Placed on <span v-text="formatDateTime(order.x.created_on)" />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
  </v-col>
  <v-col v-else>
    <v-card>
      <ac-asset :asset="null" thumb-name="thumbnail" />
      <v-card-text>
        <strong>Private Order</strong>
        <p>This order is private. No details or previews, sorry!</p>
      </v-card-text>
    </v-card>
  </v-col>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Formatting from '../mixins/formatting'
import {Prop} from 'vue-property-decorator'
import AcAsset from './AcAsset.vue'
import {SingleController} from '@/store/singles/controller'
import Order from '@/types/Order'
import Subjective from '@/mixins/subjective'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcDeliverableStatus from '@/components/AcDeliverableStatus.vue'
  @Component({
    components: {AcDeliverableStatus, AcLink, AcAsset},
  })
export default class AcOrderPreview extends mixins(Subjective, Formatting) {
    @Prop({required: true})
    public type!: string

    @Prop({required: true})
    public order!: SingleController<Order>

    public get name() {
      /* istanbul ignore if */
      if (!this.order.x) {
        return
      }
      return this.order.x.product_name
    }

    public get isBuyer() {
      const order = this.order.x as Order
      return order.buyer && order.buyer.username === this.rawViewerName
    }
}
</script>
