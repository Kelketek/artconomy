<template>
  <ac-paginated :list="list">
    <template v-slot:default>
      <v-container fluid class="pa-0" grid-list-sm>
        <v-layout row wrap>
          <v-flex xs12 sm6 md4 lg2 v-for="order in list.list" :key="order.x.id">
            <ac-order-preview :order="order" :type="type" :username="username"></ac-order-preview>
          </v-flex>
        </v-layout>
      </v-container>
    </template>
  </ac-paginated>
</template>

<script lang="ts">
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {ListController} from '@/store/lists/controller'
import {Prop} from 'vue-property-decorator'
import Order from '@/types/Order'
import AcOrderPreview from '@/components/AcOrderPreview.vue'
import {FormController} from '@/store/forms/form-controller'

  @Component({
    components: {AcOrderPreview, AcPaginated, AcLoadSection},
  })
export default class OrderList extends mixins(Subjective) {
    @Prop({required: true})
    public type!: string
    @Prop({required: true})
    public category!: string
    public list: ListController<Order> = null as unknown as ListController<Order>

    public created() {
      this.list = this.$getList(`orders__${this.username}__${this.type}__${this.category}`, {
        endpoint: `/api/sales/v1/account/${this.username}/${this.type}/${this.category}/`,
      })
    }
}
</script>
