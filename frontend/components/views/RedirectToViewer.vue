<template>
  <div />
</template>

<script setup lang="ts">
import { useViewer } from "@/mixins/viewer.ts"
import { useRoute, useRouter } from "vue-router"

import { User } from "@/store/profiles/types/main"

const props = defineProps<{ viewName: string }>()
const router = useRouter()
const route = useRoute()
const { isLoggedIn, viewer } = useViewer()
if (!isLoggedIn.value) {
  router.replace({
    name: "Login",
    query: { next: route.fullPath },
  })
} else {
  router.push({
    name: props.viewName,
    params: { username: (viewer.value as User).username },
  })
}
</script>
