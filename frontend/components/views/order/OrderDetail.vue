<template>
  <v-container v-if="isCurrentRoute">
    <ac-paginated :list="deliverables" :track-pages="true">
      <template v-slot:default>
        <ac-load-section :controller="order">
          <template v-slot:default>
            <v-row>
              <v-col cols="12" sm="6" md="4" lg="3" v-for="deliverable in deliverables.list" :key="deliverable.x.id">
                <ac-unread-marker :read="deliverable.x.read">
                  <ac-deliverable-preview :scope="$route.name" :order="order.x" :deliverable="deliverable.x" />
                </ac-unread-marker>
              </v-col>
            </v-row>
          </template>
        </ac-load-section>
      </template>
    </ac-paginated>
  </v-container>
  <router-view v-else></router-view>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import Formatting from '@/mixins/formatting'
import Ratings from '@/mixins/ratings'
import {ListController} from '@/store/lists/controller'
import Deliverable from '@/types/Deliverable'
import {SingleController} from '@/store/singles/controller'
import Order from '@/types/Order'
import {Prop} from 'vue-property-decorator'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcDeliverablePreview from '@/components/AcDeliverablePreview.vue'
import AcUnreadMarker from '@/components/AcUnreadMarker.vue'
@Component({
  components: {AcUnreadMarker, AcDeliverablePreview, AcPaginated, AcLoadSection},
})
export default class DeliverableListing extends mixins(Viewer, Formatting, Ratings) {
  @Prop({required: true})
  public orderId!: number

  public deliverables: ListController<Deliverable> = null as unknown as ListController<Deliverable>
  public order: SingleController<Order> = null as unknown as SingleController<Order>
  public get url() {
    return `/api/sales/order/${this.orderId}/`
  }

  public get isCurrentRoute() {
    return ['Order', 'Sale', 'Case'].indexOf(this.$route.name!) !== -1
  }

  public created() {
    this.order = this.$getSingle(`order${this.orderId}`, {endpoint: this.url})
    this.order.get().catch(this.setError)
    this.deliverables = this.$getList(
      `order${this.orderId}__deliverables`, {endpoint: `${this.url}deliverables/`},
    )
    this.order.get().catch(this.setError)
    this.deliverables.firstRun()
  }
}
</script>
