<template>
  <v-container fluid class="pa-0">
    <router-view v-if="!currentRoute" />
    <v-container v-else fluid>
      <ac-profile-header v-if="!store.state.iFrame" :username="username" />
      <ac-subjective-product-list :username="username" />
    </v-container>
  </v-container>
</template>

<script setup lang="ts">
import AcProfileHeader from "@/components/views/profile/AcProfileHeader.vue"
import AcSubjectiveProductList from "@/components/views/store/AcSubjectiveProductList.vue"
import { computed } from "vue"
import { useRoute } from "vue-router"
import { useStore } from "vuex"
import { ArtState } from "@/store/artState.ts"

import type { SubjectiveProps } from "@/types/main"

defineProps<SubjectiveProps>()
const store = useStore<ArtState>()
const route = useRoute()
const currentRoute = computed(
  () =>
    ["Store", "StoreiFrame", "ManageStore"].indexOf(
      String(route!.name) + "",
    ) !== -1,
)
</script>
