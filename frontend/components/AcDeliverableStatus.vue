<template>
  <v-chip :color="STATUSES[deliverable.status].color" :light="!STATUSES[deliverable.status].dark">
    <v-icon left>{{STATUSES[deliverable.status].icon}}</v-icon>
    {{STATUSES[deliverable.status].text}}
  </v-chip>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import Deliverable from '@/types/Deliverable'

@Component
export default class AcDeliverableStatus extends Vue {
  public STATUSES = {
    0: {text: 'Waiting', icon: 'schedule', color: 'white', dark: false},
    1: {text: 'NEW!', icon: 'star', color: 'primary', dark: true},
    2: {text: 'Unpaid', icon: 'credit_card', color: 'orange', dark: true},
    3: {text: 'Queued', icon: 'list', color: 'secondary', dark: true},
    4: {text: 'In Progress', icon: 'edit', color: 'info', dark: true},
    5: {text: 'Review', icon: 'visibility', color: 'yellow', dark: false},
    6: {text: 'Cancelled', icon: 'cancel', color: 'black', dark: true},
    7: {text: 'Disputed', icon: 'gavel', color: 'danger', dark: true},
    8: {text: 'Completed', icon: 'check_circle', color: 'green', dark: true},
    9: {text: 'Refunded', icon: 'assignment_return', color: 'black', dark: true},
    10: {text: 'Limbo', icon: 'question', color: 'white', dark: false},
    11: {text: 'Missed', icon: 'cancel', color: 'black', dark: true},
  }

  @Prop({required: true})
  public deliverable!: Deliverable
}
</script>
