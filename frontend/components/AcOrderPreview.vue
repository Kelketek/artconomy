<template>
  <v-col v-if="order.x && order.x.seller">
    <v-card>
      <ac-link :to="order.x.default_path">
        <ac-hidden-flag :value="order.x.private || order.x.hide_details"/>
        <ac-asset
            :asset="order.x!.display"
            thumb-name="thumbnail"
            :aspect-ratio="1"
            :terse="true"
            :allow-preview="false"
            alt=""
        />
      </ac-link>
      <v-card-text>
        <v-row dense>
          <v-col cols="12">
            <ac-deliverable-status :deliverable="{status: order.x.status}" class="ma-1"/>
          </v-col>
          <v-col cols="12">
            <ac-link :to="order.x.default_path">
              {{ name }}
            </ac-link>
            <span v-if="!isBuyer"> commissioned </span>by
            <ac-link v-if="isBuyer" :to="{name: 'Profile', params: {username: order.x.seller.username}}">
              {{ order.x.seller.username }}
            </ac-link>
            <ac-link v-else-if="order.x.buyer" :to="profileLink(order.x.buyer)">
              {{ deriveDisplayName(order.x.buyer.username) }}
            </ac-link>
            <span v-else>
                (Pending)
              </span>
          </v-col>
          <v-col cols="12" v-if="order.x.guest_email">
            <strong>{{order.x.guest_email}}</strong>
          </v-col>
          <v-col cols="12">
            Placed on <span v-text="formatDateTime(order.x.created_on)"/>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-col>
  <v-col v-else>
    <v-card>
      <ac-asset :asset="null" thumb-name="thumbnail" alt=""/>
      <v-card-text>
        <strong>Private Order</strong>
        <p>This order is private. No details or previews, sorry!</p>
      </v-card-text>
    </v-card>
  </v-col>
</template>

<script setup lang="ts">
import AcAsset from './AcAsset.vue'
import {SingleController} from '@/store/singles/controller.ts'
import Order from '@/types/Order.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcDeliverableStatus from '@/components/AcDeliverableStatus.vue'
import AcHiddenFlag from '@/components/AcHiddenFlag.vue'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {computed} from 'vue'
import {useViewer} from '@/mixins/viewer.ts'
import {deriveDisplayName, formatDateTime, profileLink} from '@/lib/otherFormatters.ts'


const props = defineProps<{type: string, order: SingleController<Order>} & SubjectiveProps>()
const {rawViewerName} = useViewer()
const name = computed(() => `${props.order.x!.product_name}`)
const isBuyer = computed(() => props.order.x!.buyer && props.order.x!.buyer.username === rawViewerName.value)
</script>
