<template>
  <v-chip
    variant="flat"
    :color="STATUSES[deliverable.status].color"
    :light="!STATUSES[deliverable.status].dark"
  >
    <v-icon
      left
      :icon="STATUSES[deliverable.status].icon"
    />
    {{ STATUSES[deliverable.status].text }}
  </v-chip>
</template>

<script setup lang="ts">
import {
  mdiCancel,
  mdiCheckCircle,
  mdiClipboardArrowLeft,
  mdiClockOutline,
  mdiCreditCard,
  mdiEye,
  mdiGavel,
  mdiHelpCircle,
  mdiListBox,
  mdiPencil,
  mdiStar,
} from '@mdi/js'

import {DeliverableStatusValue} from '@/types/main'

defineProps<{deliverable: {status: DeliverableStatusValue}}>()
const STATUSES = {
  0: {
    text: 'Waiting',
    icon: mdiClockOutline,
    color: 'white',
    dark: false,
  },
  1: {
    text: 'NEW!',
    icon: mdiStar,
    color: 'primary',
    dark: true,
  },
  2: {
    text: 'Unpaid',
    icon: mdiCreditCard,
    color: 'orange',
    dark: true,
  },
  3: {
    text: 'Queued',
    icon: mdiListBox,
    color: 'secondary',
    dark: true,
  },
  4: {
    text: 'In Progress',
    icon: mdiPencil,
    color: 'info',
    dark: true,
  },
  5: {
    text: 'Review',
    icon: mdiEye,
    color: 'yellow',
    dark: false,
  },
  6: {
    text: 'Cancelled',
    icon: mdiCancel,
    color: 'black',
    dark: true,
  },
  7: {
    text: 'Disputed',
    icon: mdiGavel,
    color: 'danger',
    dark: true,
  },
  8: {
    text: 'Completed',
    icon: mdiCheckCircle,
    color: 'green',
    dark: true,
  },
  9: {
    text: 'Refunded',
    icon: mdiClipboardArrowLeft,
    color: 'black',
    dark: true,
  },
  10: {
    text: 'Limbo',
    icon: mdiHelpCircle,
    color: 'white',
    dark: false,
  },
  11: {
    text: 'Missed',
    icon: mdiCancel,
    color: 'black',
    dark: true,
  },
}

</script>
