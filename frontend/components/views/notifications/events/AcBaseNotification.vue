<template>
  <v-list-item>
    <template #prepend>
      <ac-link
        :to="assetLink"
        class="mr-5"
      >
        <v-tooltip :text="formatDateTime(event.date)">
          <template #activator="{ props }">
            <v-badge
              left
              overlap
              :model-value="!notification.read"
              color="primary"
              v-bind="props"
            >
              <template #badge>
                <span>*</span>
              </template>
              <slot name="avatar">
                <v-avatar>
                  <img
                    :src="image"
                    alt=""
                  >
                </v-avatar>
              </slot>
            </v-badge>
          </template>
        </v-tooltip>
      </ac-link>
    </template>
    <v-list-item-title>
      <slot name="title" />
    </v-list-item-title>
    <v-list-item-subtitle>
      <slot name="subtitle" />
    </v-list-item-subtitle>
    <slot name="extra" />
  </v-list-item>
</template>

<script setup lang="ts" generic="T, D extends DisplayData">
import {DisplayData, NotificationProps, useEvent} from '../mixins/notification.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import {RouteLocationRaw} from 'vue-router'
import {useImg} from '@/plugins/shortcuts.ts'
import {formatDateTime} from '@/lib/otherFormatters.ts'

const props = defineProps<{assetLink?: RouteLocationRaw, hrefLink?: RouteLocationRaw} & NotificationProps<T, D>>()
const event = useEvent(props)
const image = useImg(event.value.data.display, 'notification', true)
</script>

<style scoped>

</style>
