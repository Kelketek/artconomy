<template>
  <ac-base-notification :notification="notification" :asset-link="productLink" :username="username">
    <template v-slot:title>
      <ac-link :to="productLink">New Product: {{event.data.product.name}}</ac-link>
    </template>
    <template v-slot:subtitle>
      <ac-link :to="productLink">By {{event.data.product.user.username}} starting at
        ${{event.data.product.starting_price}}
      </ac-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from './AcBaseNotification.vue'
import {DisplayData, NotificationProps, NotificationUser, useEvent} from '../mixins/notification.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import {computed} from 'vue'
import type {Product} from '@/types/main'

declare interface NewProduct extends DisplayData {
  product: Product,
}

const props = defineProps<NotificationProps<NotificationUser, NewProduct>>()
const event = useEvent(props)

const productLink = computed(() => ({
  name: 'Product',
  params: {
    productId: event.value.data.product.id,
    username: event.value.data.product.user.username,
  },
}))
</script>

<style scoped>

</style>
