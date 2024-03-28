<template>
  <v-container>
    <ac-profile-header :username="username"></ac-profile-header>
    <ac-paginated :list="list">
      <template v-slot:default>
        <v-container fluid class="pt-2 px-0">
          <v-row>
            <v-col cols="12" class="text-right">
              <v-btn color="green" :to="{name: 'Products', params: {username}}" variant="flat">
                <v-icon left :icon="mdiPlus"/>
                Place an order!
              </v-btn>
              <v-btn class="ml-2" @click="openListing" variant="elevated" v-if="isCurrent">
                <v-icon :icon="mdiOpenInNew"/>
                Stream list display
              </v-btn>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col cols="12" sm="6" md="4" lg="2" v-for="order in list.list" :key="order.x!.id">
              <ac-order-preview :order="order" type="sale" :username="username"/>
            </v-col>
          </v-row>
        </v-container>
      </template>
      <template v-slot:empty>
        <v-row>
          <v-col cols="12" class="text-center">
            This artist has no commissions in progress.
          </v-col>
          <v-col cols="12" class="text-center">
            <v-btn color="green" :to="{name: 'Products', params: {username}}" variant="flat">
              <v-icon left :icon="mdiPlus"/>
              Place an order!
            </v-btn>
          </v-col>
        </v-row>
      </template>
    </ac-paginated>
  </v-container>
</template>

<script setup lang="ts">
import AcProfileHeader from '@/components/views/profile/AcProfileHeader.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcOrderPreview from '@/components/AcOrderPreview.vue'
import Order from '@/types/Order.ts'
import {mdiOpenInNew, mdiPlus} from '@mdi/js'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import {useSubject} from '@/mixins/subjective.ts'

const {setError} = useErrorHandling()
const props = defineProps<SubjectiveProps>()
const {isCurrent} = useSubject(props)

const openListing = () => {
  const params = 'scrollbars=no,resizable=yes,status=no,location=no,toolbar=no,menubar=no,width=200,height=300,left=100,top=100'
  open(`/store/${props.username}/queue-listing/`, 'test', params)
}

const list = useList<Order>(`${props.username}__queue`, {
  endpoint: `/api/sales/account/${props.username}/queue/`,
})
list.get().catch(setError)
</script>
