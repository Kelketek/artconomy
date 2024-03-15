<template>
  <v-container>
    <v-row no-gutters>
      <v-col>
        <v-card>
          <v-card-text>
            <p>This page has moved. Redirecting you...</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import {RouteLocationRaw, useRouter} from 'vue-router'
import {onMounted} from 'vue'

const router = useRouter()

const props = defineProps<{route: RouteLocationRaw}>()

onMounted(() => {
  router.push(props.route)
})
</script>
