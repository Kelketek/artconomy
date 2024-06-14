<template>
  <v-col>
    <v-card>
      <ac-link :to="deliverableLink">
        <ac-asset
            :asset="deliverable.display || null"
            thumb-name="thumbnail"
            :aspect-ratio="1"
            :allow-preview="false"
            :alt="`Current progress image for deliverable #${deliverable.id}`"
        />
      </ac-link>
      <v-card-text>
        <v-row dense>
          <v-col cols="12">
            <ac-link :to="deliverableLink">
              {{deliverable.name}}
            </ac-link>
          </v-col>
          <v-col cols="12" class="text-center">
            <ac-deliverable-status :deliverable="deliverable"/>
          </v-col>
          <v-col cols="12">
            Created on <span v-text="formatDateTime(deliverable.created_on)"/>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-col>
</template>

<script setup lang="ts">
import Deliverable from '@/types/Deliverable.ts'
import Order from '@/types/Order.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAsset from '@/components/AcAsset.vue'
import AcDeliverableStatus from '@/components/AcDeliverableStatus.vue'
import {formatDateTime} from '@/lib/otherFormatters.ts'
import {computed} from 'vue'

declare interface AcDeliverablePreviewProps {
  deliverable: Deliverable,
  order: Order,
  scope: string,
}

const props = defineProps<AcDeliverablePreviewProps>()

const deliverableLink = computed(() => ({
  name: `${props.scope}Deliverable`,
  params: {
    orderId: props.order.id,
    deliverableId: props.deliverable.id,
  }
}))
</script>
