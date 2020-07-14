<template>
  <v-container fluid :class="{'pa-0': !salesWaiting}">
    <v-row v-if="salesWaiting">
      <v-col cols="12" class="text-center">
        <ac-bound-field :field="searchForm.fields.q" prepend-icon="search" auto-focus
                        label="Search Waitlist"
        />
      </v-col>
    </v-row>
    <ac-paginated :list="list">
      <template v-slot:default>
        <v-container fluid class="pa-0">
          <v-row no-gutters  >
            <v-col cols="12" sm="6" md="4" lg="2" v-for="order in list.list" :key="order.x.id">
              <ac-order-preview :order="order" :type="type" :username="username"></ac-order-preview>
            </v-col>
          </v-row>
        </v-container>
      </template>
    </ac-paginated>
  </v-container>
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
import {RawData} from '@/store/forms/types/RawData'
import {Cancelable, debounce} from 'lodash'
import SearchField from '@/components/views/search/mixins/SearchField'
import AcBoundField from '@/components/fields/AcBoundField'

@Component({
  components: {AcBoundField, AcOrderPreview, AcPaginated, AcLoadSection},
})
export default class OrderList extends mixins(Subjective, SearchField) {
    @Prop({required: true})
    public type!: string

    @Prop({required: true})
    public category!: string

    public list: ListController<Order> = null as unknown as ListController<Order>
    public debouncedUpdate!: ((newData: RawData) => void) & Cancelable
    public searchForm: FormController = null as unknown as FormController

    public get salesWaiting() {
      return (this.type === 'sales') && (this.category === 'waiting')
    }

    public created() {
      this.searchForm = this.$getForm('waitlistSearch', {endpoint: '#', fields: {q: {value: ''}}})
      this.list = this.$getList(`orders__${this.username}__${this.type}__${this.category}`, {
        endpoint: `/api/sales/v1/account/${this.username}/${this.type}/${this.category}/`,
      })
    }
}
</script>
