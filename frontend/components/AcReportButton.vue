<template>
  <v-btn @click="store.commit('reportDialog', true)">
    <v-icon left> {{ mdiFlag }} </v-icon>Report
  </v-btn>
</template>

<script setup lang="ts">
import { mdiFlag } from "@mdi/js"
import { ArtState } from "@/store/artState.ts"
import { useStore } from "vuex"

const store = useStore<ArtState>()
</script>
