<template>
  <v-row dense v-if="reference">
    <v-col cols="12">
      <ac-unread-marker :read="reference.read">
        <div class="pop-out-container">
          <v-btn icon absolute left color="secondary" variant="flat" class="pop-out-button" @click="refTab">
            <v-icon :icon="mdiTab"/>
          </v-btn>
          <ac-link
              :to="{name: `${baseName}DeliverableReference`, params: {...route.params, referenceId: reference.id}}">
            <ac-asset :asset="reference" thumb-name="thumbnail" alt="Reference image for order. Click to read comments."/>
          </ac-link>
        </div>
      </ac-unread-marker>
    </v-col>
  </v-row>
</template>

<style scoped>
.pop-out-container {
  position: relative;
}
.pop-out-button {
  position: absolute;
  top: 4px;
  left: 4px;
  z-index: 1;
}
</style>

<script setup lang="ts">
import AcUnreadMarker from '@/components/AcUnreadMarker.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAsset from '@/components/AcAsset.vue'
import Reference from '@/types/Reference.ts'
import {mdiTab} from '@mdi/js'
import {useRoute} from 'vue-router'

const route = useRoute()
const props = defineProps<{reference: Reference, baseName: string}>()
const refTab = () => window.open(props.reference.file.full, '_blank')
</script>
