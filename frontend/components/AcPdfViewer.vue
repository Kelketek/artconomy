<template>
  <v-row class="my-1">
    <ac-pdf-nav v-model="page" :pages="pages" />
    <v-col class="d-flex justify-center" cols="12">
      <VuePDF :pdf="pdf" :page="page" fit-parent />
    </v-col>
    <ac-pdf-nav v-model="page" :pages="pages" />
  </v-row>
</template>

<script setup lang="ts">
const props = defineProps<{ asset: Asset }>()

import { VuePDF, usePDF } from "@tato30/vue-pdf"
import { ref } from "vue"
import AcPdfNav from "@/components/AcPdfNav.vue"
import type { Asset } from "@/types/main"

const page = ref(1)

const { pdf, pages } = usePDF(props.asset.file!.full)
</script>
