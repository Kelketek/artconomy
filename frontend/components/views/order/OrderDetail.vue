<template>
  <v-container v-if="isCurrentRoute">
    <ac-paginated :list="deliverables" :track-pages="true">
      <template #default>
        <ac-load-section :controller="order">
          <template #default>
            <v-row>
              <v-col
                v-for="deliverable in deliverables.list"
                :key="deliverable.x!.id"
                cols="12"
                sm="6"
                md="4"
                lg="3"
              >
                <ac-unread-marker :read="deliverable.x!.read">
                  <ac-deliverable-preview
                    :scope="String(route.name)"
                    :order="order.x!"
                    :deliverable="deliverable.x!"
                  />
                </ac-unread-marker>
              </v-col>
            </v-row>
          </template>
        </ac-load-section>
      </template>
    </ac-paginated>
  </v-container>
  <router-view v-else />
</template>

<script setup lang="ts">
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcPaginated from "@/components/wrappers/AcPaginated.vue"
import AcDeliverablePreview from "@/components/AcDeliverablePreview.vue"
import AcUnreadMarker from "@/components/AcUnreadMarker.vue"
import { computed } from "vue"
import { useSingle } from "@/store/singles/hooks.ts"
import { useRoute, useRouter } from "vue-router"
import { useErrorHandling } from "@/mixins/ErrorHandling.ts"
import { useList } from "@/store/lists/hooks.ts"
import { useViewer } from "@/mixins/viewer.ts"
import type { Deliverable, Order, OrderProps } from "@/types/main"
import { requireAuth } from "@/components/views/order/mixins/DeliverableMixin.ts"

const props = defineProps<OrderProps>()
const route = useRoute()
const router = useRouter()

const isCurrentRoute = computed(() => {
  return ["Order", "Sale", "Case"].indexOf(String(route.name)) !== -1
})

const url = computed(() => {
  return `/api/sales/order/${props.orderId}/`
})

const { setError } = useErrorHandling()
const { isLoggedIn } = useViewer()

const order = useSingle<Order>(`order${props.orderId}`, {
  endpoint: url.value,
})
const handleError = requireAuth(router, isLoggedIn)
order.get().catch(handleError).catch(setError)
const deliverables = useList<Deliverable>(
  `order${props.orderId}__deliverables`,
  { endpoint: `${url.value}deliverables/` },
)
deliverables.firstRun().catch(handleError)
</script>
