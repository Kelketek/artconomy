<template>
  <v-list-item v-if="link.x">
    <template #prepend>
      <v-avatar v-if="!logoFailed">
        <v-img :src="favicon" @error="() => (logoFailed = true)" />
      </v-avatar>
      <v-avatar v-else variant="elevated">
        <v-icon>
          {{ mdiAccount }}
        </v-icon>
      </v-avatar>
    </template>
    <v-list-item-title>
      <ac-link :to="siteLink" :new-tab="true"> {{ link.x.site_name }} </ac-link
      ><span v-if="link.x.identifier">: </span
      ><ac-link v-if="link.x.identifier" :to="accountUrl" :new-tab="true">
        {{ link.x.identifier }}
      </ac-link>
    </v-list-item-title>
    <template #append>
      <v-list-item-action end>
        <v-btn
          icon
          color="red"
          size="small"
          aria-label="Delete"
          @click="link.delete"
        >
          <v-icon size="x-large">
            {{ mdiDelete }}
          </v-icon>
        </v-btn>
      </v-list-item-action>
    </template>
  </v-list-item>
</template>

<script setup lang="ts">
import { SingleController } from "@/store/singles/controller.ts"
import { SocialLink } from "@/types/main"
import { computed, ref } from "vue"
import AcLink from "@/components/wrappers/AcLink.vue"
import { mdiAccount, mdiDelete } from "@mdi/js"

const props = defineProps<{
  link: SingleController<SocialLink>
  controls: boolean
}>()
const url = computed(() => new URL(props.link.x!.url))
const logoFailed = ref(false)
const siteLink = computed(() => {
  if (!props.link.x!.identifier) {
    return url.value
  }
  return null
})
const accountUrl = computed(() => {
  if (url.value.pathname === "/") {
    // Happens for cases like Carrd.co where there's no username but there is a subdomain.
    return null
  }
  return url.value.toString()
})
const favicon = computed(
  () => `https://favicon.twenty.com/${url.value.hostname}`,
)
</script>

<style scoped></style>
