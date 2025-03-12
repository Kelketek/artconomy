<template>
  <v-row id="avatar-settings">
    <v-col
      class="text-center"
      cols="12"
      sm="3"
      lg="3"
      offset-sm="2"
      offset-lg="3"
      align-self="center"
    >
      <v-card>
        <v-card-text>
          <v-list-subheader>Current Avatar</v-list-subheader>
          <img
            class="avatar-preview shadowed pt-3"
            :src="subject!.avatar_url"
            :alt="subject!.username"
          />
          <p v-if="subject!.avatar_url.indexOf('gravatar') > -1">
            Default avatars provided by
            <a href="http://en.gravatar.com/">Gravatar</a>
          </p>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" sm="6" lg="3">
      <ac-uppy-file
        uppy-id="uppy-avatar"
        :endpoint="url"
        label="Upload a new Avatar"
      />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue"
import { listenForSingle } from "@/store/singles/hooks.ts"
import { useSubject } from "@/mixins/subjective.ts"
import type { SubjectiveProps } from "@/types/main"
const AcUppyFile = defineAsyncComponent(
  () => import("@/components/fields/AcUppyFile.vue"),
)

const props = defineProps<SubjectiveProps>()
const { subject } = useSubject({ props })
listenForSingle("uppy-avatar")

const url = computed(() => `/api/profiles/account/${props.username}/avatar/`)
</script>

<style scoped></style>
