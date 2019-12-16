<template>
  <v-col>
      <v-card>
        <ac-link :to="orderLink">
          <ac-asset :asset="order.x.display" thumb-name="thumbnail" />
        </ac-link>
        <v-card-text>
          <v-row dense>
            <v-col cols="12">
              <ac-link :to="orderLink">
                {{ name }}</ac-link>
              <span v-if="!isBuyer">commissioned </span>by
              <ac-link v-if="isBuyer" :to="{name: 'Profile', params: {username: order.x.seller.username}}">
                {{ order.x.seller.username }}</ac-link>
              <ac-link v-else-if="order.x.buyer" :to="buyerProfile">
                {{ deriveDisplayName(order.x.buyer.username) }}</ac-link>
              <span v-else>
                (Pending)
              </span>
            </v-col>
            <v-col cols="12" class="text-center">
              <ac-order-status :order="order.x" />
            </v-col>
            <v-col cols="12">
              Placed on <span v-text="formatDateTime(order.x.created_on)" />
            </v-col>
          </v-row>
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
import AcOrderStatus from '@/components/AcOrderStatus.vue'
  @Component({
    components: {AcOrderStatus, AcLink, AcAsset},
  })
export default class AcOrderPreview extends mixins(Subjective, Formatting) {
    @Prop({required: true})
    public type!: string
    @Prop({required: true})
    public order!: SingleController<Order>

    public get orderLink() {
      const order = this.order.x as Order
      return {name: this.routeName, params: {username: this.username, orderId: order.id}}
    }

    public get name() {
      if (!this.order.x) {
        return
      }
      if (!this.order.x.product) {
        return '(Custom Project)'
      }
      return this.order.x.product.name
    }

    public get isBuyer() {
      const order = this.order.x as Order
      return order.buyer && order.buyer.username === this.rawViewerName
    }

    public get buyerProfile() {
      const order = this.order.x as Order
      if (!order.buyer) {
        return null
      }
      if (this.guestName(order.buyer.username)) {
        return null
      }
      return {name: 'Profile', params: {username: order.buyer.username}}
    }

    public get routeName() {
      // In: 'sales'
      // Out: 'Sale'
      return this.type[0].toUpperCase() + this.type.slice(1, this.type.length - 1)
    }
}
</script>
