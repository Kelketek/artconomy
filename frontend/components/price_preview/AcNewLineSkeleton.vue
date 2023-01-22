<template>
  <v-row no-gutters>
    <v-col cols="2" />
    <v-col cols="4">
      <v-skeleton-loader type="list-item" />
    </v-col>
    <v-col cols="4">
      <v-skeleton-loader type="list-item" />
    </v-col>
    <v-col cols="2">
      <v-skeleton-loader type="list-item" />
    </v-col>
  </v-row>
</template>

<script>
import Vue from 'vue'
import Component from 'vue-class-component'

@Component
export default class AcNewLineSkeleton extends Vue {}
</script>
