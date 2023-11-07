<template>
  <v-chip variant="flat" :color="STATUSES[deliverable.status].color" :light="!STATUSES[deliverable.status].dark">
    <v-icon left :icon="STATUSES[deliverable.status].icon"/>
    {{STATUSES[deliverable.status].text}}
  </v-chip>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import Deliverable from '@/types/Deliverable'

@Component
class AcDeliverableStatus extends Vue {
  public STATUSES = {
    0: {
      text: 'Waiting',
      icon: 'mdi-clock-outline',
      color: 'white',
      dark: false,
    },
    1: {
      text: 'NEW!',
      icon: 'mdi-star',
      color: 'primary',
      dark: true,
    },
    2: {
      text: 'Unpaid',
      icon: 'mdi-credit-card',
      color: 'orange',
      dark: true,
    },
    3: {
      text: 'Queued',
      icon: 'mdi-list-box',
      color: 'secondary',
      dark: true,
    },
    4: {
      text: 'In Progress',
      icon: 'mdi-pencil',
      color: 'info',
      dark: true,
    },
    5: {
      text: 'Review',
      icon: 'mdi-eye',
      color: 'yellow',
      dark: false,
    },
    6: {
      text: 'Cancelled',
      icon: 'mdi-cancel',
      color: 'black',
      dark: true,
    },
    7: {
      text: 'Disputed',
      icon: 'mdi-gavel',
      color: 'danger',
      dark: true,
    },
    8: {
      text: 'Completed',
      icon: 'mdi-check-circle',
      color: 'green',
      dark: true,
    },
    9: {
      text: 'Refunded',
      icon: 'mdi-clipboard-arrow-left',
      color: 'black',
      dark: true,
    },
    10: {
      text: 'Limbo',
      icon: 'mdi-question-mark-circle',
      color: 'white',
      dark: false,
    },
    11: {
      text: 'Missed',
      icon: 'mdi-cancel',
      color: 'black',
      dark: true,
    },
  }

  @Prop({required: true})
  public deliverable!: Deliverable
}

export default toNative(AcDeliverableStatus)
</script>
