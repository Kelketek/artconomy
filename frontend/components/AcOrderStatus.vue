<template>
  <v-chip :color="STATUSES[order.status].color" :light="!STATUSES[order.status].dark">
    <v-icon left>{{STATUSES[order.status].icon}}</v-icon>
      {{STATUSES[order.status].text}}
  </v-chip>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import Order from '../types/Order'

@Component
export default class AcOrderStatus extends Vue {
  public STATUSES = {
    1: {text: 'NEW!', icon: 'star', color: 'primary', dark: true},
    2: {text: 'Unpaid', icon: 'credit_card', color: 'orange', dark: true},
    3: {text: 'Queued', icon: 'list', color: 'secondary', dark: true},
    4: {text: 'In Progress', icon: 'edit', color: 'info', dark: true},
    5: {text: 'Review', icon: 'visibility', color: 'yellow', dark: false},
    6: {text: 'Cancelled', icon: 'cancel', color: 'black', dark: true},
    7: {text: 'Disputed', icon: 'gavel', color: 'danger', dark: true},
    8: {text: 'Completed', icon: 'check_circle', color: 'green', dark: true},
    9: {text: 'Refunded', icon: 'assignment_return', color: 'black', dark: true},
  }
  @Prop({required: true})
  public order!: Order
}
</script>
